import re

from ftrs_common.feature_flags import FeatureFlag, is_enabled
from ftrs_data_layer.domain import (
    HealthcareServiceCategory,
    HealthcareServiceType,
    Organisation,
)
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.domain.enums import OrganisationType

from service_migration.transformer.base import (
    ServiceTransformer,
    ServiceTransformOutput,
)

PHARMACY_TYPE_TO_ORGANISATION_TYPE: dict[int, OrganisationType] = {
    13: OrganisationType.COMMUNITY_PHARMACY,
    134: OrganisationType.DISTANCE_SELLING_PHARMACY,
}


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
        Override to map to new service types
        and explicitly exclude endpoints from pharmacy organisations.
        """
        organisation = super().build_organisation(service)
        organisation_type = PHARMACY_TYPE_TO_ORGANISATION_TYPE.get(service.typeid)
        return organisation.model_copy(
            update={
                "endpoints": [],
                "type": organisation_type,
            }
        )

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
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        if service.statusid != cls.STATUS_ACTIVE:
            return False, "Service is not active"

        return True, None
