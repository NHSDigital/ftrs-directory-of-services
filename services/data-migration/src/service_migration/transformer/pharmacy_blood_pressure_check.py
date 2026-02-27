from collections.abc import Callable
from uuid import UUID

from ftrs_common.feature_flags import FeatureFlag, is_enabled
from ftrs_common.logger import Logger
from ftrs_data_layer.domain import HealthcareServiceCategory, HealthcareServiceType
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.logbase import DataMigrationLogBase
from sqlalchemy import Engine
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from common.cache import DoSMetadataCache
from service_migration.exceptions import ParentPharmacyNotFoundError
from service_migration.models import ServiceMigrationState
from service_migration.transformer.base import (
    LinkedPharmacyTransformer,
    ServiceTransformOutput,
)
from service_migration.transformer.base_pharmacy import BasePharmacyTransformer


class BasePharmacyBPCheckTransformer(LinkedPharmacyTransformer):
    STATUS_ACTIVE = 1
    ODS_BASE_LENGTH = 5
    NAME_PREFIXES = ("BP Check:", "BP:")
    SERVICE_TYPE_ID: int
    ODS_SUFFIX: str

    """
    Base transformer for Pharmacy Blood Pressure Check services linked to parent pharmacies.

    Selection criteria:
    - The service type must match the BP Check pharmacy type for the subclass
    - The service must have an ODS code ending with the subclass suffix
    - The service name must be prefixed with "BP Check:" or "BP:"

    Filter criteria:
    - The service must be active

    Parent pharmacy resolution:
    - The BP suffix is removed to derive the base 5-character ODS code
    - The parent pharmacy is looked up by base ODS code and matching pharmacy type
    - If a parent state record already exists, its organisation/location IDs are reused
    - If no state record exists, the parent pharmacy is migrated first (transaction 1)
        and the resulting org/location IDs are used for the BP check service (transaction 2)
    - If no parent pharmacy record exists in DoS at all, the service is rejected

    Feature flag behavior:
    - When data_migration_pharmacy_enabled is disabled:
        Service is not supported (no records created)
    - When enabled: A HealthcareService of type Essential Services is created and linked
        to the parent pharmacy organisation and location
    """

    def __init__(self, logger: Logger, metadata: DoSMetadataCache) -> None:
        super().__init__(logger=logger, metadata=metadata)
        self.parent_organisation_id: UUID | None = None
        self.parent_location_id: UUID | None = None

    def transform(self, service: legacy_model.Service) -> ServiceTransformOutput:
        healthcare_service = self.build_healthcare_service(
            service,
            self.parent_organisation_id,
            self.parent_location_id,
            category=HealthcareServiceCategory.PHARMACY_SERVICES,
            type=HealthcareServiceType.ESSENTIAL_SERVICES,
        )

        return ServiceTransformOutput(
            organisation=[],
            healthcare_service=[healthcare_service],
            location=[],
        )

    def resolve_parent(
        self,
        service: legacy_model.Service,
        engine: Engine,
        get_state_record: Callable[[int], ServiceMigrationState | None],
    ) -> tuple[legacy_model.Service | None, UUID | None, UUID | None]:
        """
        Resolve the parent pharmacy organisation and location for a BP check service.

        Derives the base ODS code by stripping the BP suffix, then:
        1. Queries the legacy DB for a parent pharmacy service with that base ODS code
        2. If found, checks the state table for an already-migrated state record
        3. If a state record exists, returns (None, org_id, loc_id) — no migration needed
        4. If no state record, returns (parent_service, None, None) — processor migrates parent first
        5. If no parent pharmacy exists in DoS at all, raises ParentPharmacyNotFoundError

        :param service: The BP check legacy service being processed
        :param engine: SQLAlchemy engine for querying the legacy DoS database
        :param get_state_record: Callable to fetch migration state by legacy service ID
        :return: Tuple of (parent_legacy_service_or_None, org_id_or_None, loc_id_or_None)
        :raises ParentPharmacyNotFoundError: When no parent pharmacy record exists in DoS
        """
        base_ods_code = service.odscode[: -len(self.ODS_SUFFIX)]

        parent_service = self._find_parent_service(engine, base_ods_code)

        if parent_service is None:
            self.logger.log(
                DataMigrationLogBase.DM_ETL_038,
                service_id=service.id,
                base_ods_code=base_ods_code,
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
        Query the legacy DoS database for a pharmacy service matching the base ODS code.
        All relationships (including nested ones) are eagerly loaded via selectinload so
        the returned object is fully usable after the session closes.
        """
        stmt = (
            select(legacy_model.Service)
            .where(legacy_model.Service.odscode == base_ods_code)
            .where(legacy_model.Service.typeid == self.SERVICE_TYPE_ID)
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
    def is_service_supported(  # noqa: PLR0911
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        if not is_enabled(FeatureFlag.DATA_MIGRATION_PHARMACY_ENABLED):
            return (
                False,
                "Pharmacy service selection is disabled by feature flag",
            )

        if service.typeid != cls.SERVICE_TYPE_ID:
            return (
                False,
                f"Service type is not a Pharmacy type ({cls.SERVICE_TYPE_ID})",
            )

        if not service.odscode:
            return False, "Service does not have an ODS code"

        expected_length = cls.ODS_BASE_LENGTH + len(cls.ODS_SUFFIX)
        if len(service.odscode) != expected_length:
            return False, f"ODS code is not {expected_length} characters"

        if not service.odscode.endswith(cls.ODS_SUFFIX):
            return False, f"ODS code does not end with {cls.ODS_SUFFIX}"

        base_ods_code = service.odscode[: cls.ODS_BASE_LENGTH]
        matches_f_prefix = (
            BasePharmacyTransformer.PHARMACY_ODS_CODE_REGEX_F_PREFIX.match(
                base_ods_code
            )
        )
        matches_alternating = (
            BasePharmacyTransformer.PHARMACY_ODS_CODE_REGEX_ALTERNATING.match(
                base_ods_code
            )
        )

        if not (matches_f_prefix or matches_alternating):
            return (
                False,
                "ODS code does not match required format (F + 4 alphanumeric OR alternating letter-number)",
            )

        return True, None

    @classmethod
    def should_include_service(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        if service.statusid != cls.STATUS_ACTIVE:
            return False, "Service is not active"

        if not service.name:
            return False, "Service name is missing"

        if not any(service.name.startswith(prefix) for prefix in cls.NAME_PREFIXES):
            return (
                False,
                "Service name does not start with required prefix (BP Check: or BP:)",
            )

        return True, None


class PharmacyBPCheckTransformer(BasePharmacyBPCheckTransformer):
    """
    Transformer for Pharmacy Blood Pressure Check services.

    Selection criteria:
    - The service type must be "Pharmacy Blood Pressure Check" (148)
    - The service must have an ODS code ending with "BPS"
    - The service name must be prefixed with "BP Check:" or "BP:"
    """

    SERVICE_TYPE_ID = 148
    ODS_SUFFIX = "BPS"


class PharmacyDSPBPCheckTransformer(BasePharmacyBPCheckTransformer):
    """
    Transformer for Pharmacy Blood Pressure Check services with DSP suffix.

    Selection criteria:
    - The service type must be "Pharmacy DSP Blood Pressure Check" (134)
    - The service must have an ODS code ending with "DSPBPS"
    - The service name must be prefixed with "BP Check:" or "BP:"
    """

    SERVICE_TYPE_ID = 134
    ODS_SUFFIX = "DSPBPS"
