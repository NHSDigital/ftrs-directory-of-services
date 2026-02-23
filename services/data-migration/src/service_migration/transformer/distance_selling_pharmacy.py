import re

from ftrs_common.feature_flags import FeatureFlag, is_enabled
from ftrs_data_layer.domain import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)
from ftrs_data_layer.domain import legacy as legacy_model

from service_migration.transformer.base import (
    ServiceTransformer,
    ServiceTransformOutput,
)


class DistanceSellingPharmacyTransformer(ServiceTransformer):
    STATUS_ACTIVE = 1
    DISTANCE_SELLING_PHARMACY_TYPE_ID = 134
    PHARMACY_ODS_CODE_REGEX_F_PREFIX = re.compile(r"^F[A-Z0-9]{4}$")
    PHARMACY_ODS_CODE_REGEX_ALTERNATING = re.compile(r"^[A-Z][0-9][A-Z][0-9][A-Z]$")

    """
    Transformer for Distance Selling Pharmacy services.

    Selection criteria:
    - The service type must be 'Pharmacy Distance Selling' (134)
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

    Note: Pharmacies do NOT have endpoints in the source data, so endpoints array will be empty.
    """

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
                "Distance Selling Pharmacy service selection is disabled by feature flag",
            )

        if service.typeid != cls.DISTANCE_SELLING_PHARMACY_TYPE_ID:
            return False, "Service type is not Pharmacy Distance Selling (134)"

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
