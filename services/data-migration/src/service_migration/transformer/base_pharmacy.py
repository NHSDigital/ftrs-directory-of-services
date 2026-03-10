import re
from collections.abc import Callable
from typing import TYPE_CHECKING
from uuid import UUID

from ftrs_common.feature_flags import FeatureFlag, is_enabled
from ftrs_common.logger import Logger
from ftrs_data_layer.domain import (
    HealthcareServiceCategory,
    HealthcareServiceType,
    Organisation,
)
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.logbase import DataMigrationLogBase
from sqlalchemy import Engine
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from common.cache import DoSMetadataCache
from service_migration.exceptions import ParentPharmacyNotFoundError
from service_migration.transformer.base import (
    ServiceTransformer,
    ServiceTransformOutput,
)

if TYPE_CHECKING:
    from service_migration.models import ServiceMigrationState


class BasePharmacyTransformer(ServiceTransformer):
    STATUS_ACTIVE = 1
    PHARMACY_TYPE_IDS = frozenset({13, 134})
    PHARMACY_ODS_CODE_REGEX_F_PREFIX = re.compile(r"^F[A-Z0-9]{4}$")
    PHARMACY_ODS_CODE_REGEX_ALTERNATING = re.compile(r"^[A-Z][0-9][A-Z][0-9][A-Z]$")

    """
    Transformer for Pharmacy services (Community Pharmacy and Distance Selling Pharmacy).

    Selection criteria:
    - The service type must be 'Pharmacy' (13) or 'Pharmacy Distance Selling' (134)
    - The service must have an ODS code
    - The ODS code should be 5 characters
    - The ODS code format should either:
      - Start with 'F' followed by 4 alphanumeric characters (e.g., FXX99)
      - Follow alternating alpha-numeric pattern: letter-number-letter-number-letter (e.g., A1B2C)

    Filter criteria:
    - The service must be active

    Feature flag behavior:
    - When data_migration_pharmacy_enabled is disabled:
      Service is not supported (no records created)
    - When enabled: All resources (organisation, location, healthcare_service) are created
    """

    def build_organisation(self, service: legacy_model.Service) -> Organisation:
        """
        Override to explicitly exclude endpoints from pharmacy organisations.
        Type is resolved from SERVICE_TYPE_TO_ORGANISATION_TYPE in the base transformer.
        """
        organisation = super().build_organisation(service)
        return organisation.model_copy(update={"endpoints": []})

    def transform(self, service: legacy_model.Service) -> ServiceTransformOutput:
        organisation = self.build_organisation(service)
        location = self.build_location(service, organisation.id)
        healthcare_service = self.build_healthcare_service(
            service,
            organisation.id,
            location.id,
            category=HealthcareServiceCategory.PHARMACY_SERVICES,
            type=HealthcareServiceType.ESSENTIAL_SERVICES,
        )

        return ServiceTransformOutput(
            organisation=[organisation],
            healthcare_service=[healthcare_service],
            location=[location],
        )

    @classmethod
    def is_service_supported(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        ods_code_length = 5

        if not is_enabled(FeatureFlag.DATA_MIGRATION_PHARMACY_ENABLED):
            return (
                False,
                "Pharmacy service selection is disabled by feature flag",
            )

        if service.typeid not in cls.PHARMACY_TYPE_IDS:
            return (
                False,
                f"Service type is not a Pharmacy type ({', '.join(map(str, sorted(cls.PHARMACY_TYPE_IDS)))})",
            )

        if not service.odscode:
            return False, "Service does not have an ODS code"

        if len(service.odscode) != ods_code_length:
            return False, "ODS code is not 5 characters"

        matches_f_prefix = cls.PHARMACY_ODS_CODE_REGEX_F_PREFIX.match(service.odscode)
        matches_alternating = cls.PHARMACY_ODS_CODE_REGEX_ALTERNATING.match(
            service.odscode
        )

        if not (matches_f_prefix or matches_alternating):
            return (
                False,
                "ODS code does not match required format (F + 4 alphanumeric OR alternating letter-number)",
            )

        return True, None

    @classmethod
    def should_include_service(
        cls,
        service: legacy_model.Service,
        state_record: "ServiceMigrationState | None" = None,
    ) -> tuple[bool, str | None]:
        if service.statusid != cls.STATUS_ACTIVE:
            if state_record is not None:
                return True, None
            return False, "Service is not active"

        return True, None


class LinkedPharmacyTransformer(ServiceTransformer):
    """
    Base class for transformers that create a service linked to a separately-migrated
    parent pharmacy organisation/location.
    """

    STATUS_ACTIVE = 1
    PARENT_PHARMACY_TYPE_IDS = BasePharmacyTransformer.PHARMACY_TYPE_IDS
    ODS_SUFFIX = ""
    HEALTHCARE_SERVICE_CATEGORY = HealthcareServiceCategory.PHARMACY_SERVICES
    HEALTHCARE_SERVICE_TYPE: HealthcareServiceType

    def __init__(self, logger: Logger, metadata: DoSMetadataCache) -> None:
        super().__init__(logger=logger, metadata=metadata)
        self.parent_organisation_id: UUID | None = None
        self.parent_location_id: UUID | None = None

    def transform(self, service: legacy_model.Service) -> ServiceTransformOutput:
        healthcare_service = self.build_healthcare_service(
            service,
            self.parent_organisation_id,
            self.parent_location_id,
            category=self.HEALTHCARE_SERVICE_CATEGORY,
            type=self.HEALTHCARE_SERVICE_TYPE,
        )

        return ServiceTransformOutput(
            organisation=[],
            location=[],
            healthcare_service=[healthcare_service],
        )

    def resolve_parent(
        self,
        service: legacy_model.Service,
        engine: Engine,
        get_state_record: Callable[[int], "ServiceMigrationState | None"],
    ) -> tuple[legacy_model.Service | None, UUID | None, UUID | None]:
        """
        Resolve the parent pharmacy organisation and location for a linked service.
        """
        base_ods_code = (
            service.odscode[: -len(self.ODS_SUFFIX)]
            if self.ODS_SUFFIX
            else service.odscode
        )

        parent_service = self._find_parent_service(engine, base_ods_code)

        if parent_service is None:
            self.logger.log(
                DataMigrationLogBase.DM_ETL_038,
                record_id=service.id,
                ods_code=base_ods_code,
            )
            raise ParentPharmacyNotFoundError(
                record_id=service.id,
                ods_code=base_ods_code,
            )

        state_record = get_state_record(parent_service.id)

        if state_record is not None:
            return None, state_record.organisation_id, state_record.location_id

        return parent_service, None, None

    def _find_parent_service(
        self, engine: Engine, base_ods_code: str
    ) -> legacy_model.Service | None:
        """
        Query the legacy DoS database for an active parent pharmacy service matching
        the derived base ODS code.

        All required relationships (including nested opening-time relationships) are
        eagerly loaded via selectinload so the returned object is fully usable after
        the session closes.
        """
        stmt = (
            select(legacy_model.Service)
            .where(legacy_model.Service.odscode == base_ods_code)
            .where(legacy_model.Service.typeid.in_(self.PARENT_PHARMACY_TYPE_IDS))
            .where(legacy_model.Service.statusid == self.STATUS_ACTIVE)
            .options(
                selectinload(legacy_model.Service.endpoints),
                selectinload(legacy_model.Service.scheduled_opening_times).selectinload(
                    legacy_model.ServiceDayOpening.times
                ),
                selectinload(legacy_model.Service.specified_opening_times).selectinload(
                    legacy_model.ServiceSpecifiedOpeningDate.times
                ),
                selectinload(legacy_model.Service.sgsds),
                selectinload(legacy_model.Service.dispositions),
                selectinload(legacy_model.Service.age_range),
            )
            .limit(1)
        )
        with Session(engine) as session:
            return session.scalars(stmt).first()

    @classmethod
    def should_include_service(
        cls,
        service: legacy_model.Service,
        state_record: "ServiceMigrationState | None" = None,
    ) -> tuple[bool, str | None]:
        if service.statusid != cls.STATUS_ACTIVE:
            if state_record is not None:
                return True, None
            return False, "Service is not active"

        return True, None
