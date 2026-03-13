from typing import TYPE_CHECKING

from ftrs_common.feature_flags import FeatureFlag, is_enabled
from ftrs_data_layer.domain import HealthcareServiceType
from ftrs_data_layer.domain import legacy as legacy_model

if TYPE_CHECKING:
    from service_migration.models import ServiceMigrationState

from service_migration.transformer.base_pharmacy import (
    BasePharmacyTransformer,
    LinkedPharmacyTransformer,
)


class PharmacyBPCheckTransformer(LinkedPharmacyTransformer):
    STATUS_ACTIVE = 1
    ODS_BASE_LENGTH = 5
    NAME_PREFIXES = ("BP Check:", "BP:")
    SERVICE_TYPE_ID = 148
    ODS_SUFFIX = "BPS"
    HEALTHCARE_SERVICE_TYPE = HealthcareServiceType.BLOOD_PRESSURE_CHECK

    """
    Transformer for Pharmacy Blood Pressure Check services.

    Selection criteria:
    - The service type must be "Pharmacy Blood Pressure Check" (148)
    - The service must have an ODS code ending with "BPS"
    - The service name must be prefixed with "BP Check:" or "BP:"

    Filter criteria:
    - By default, the service must be active
    - Inactive services are still included when a migration state record already exists

    Parent pharmacy resolution:
    - The ODS suffix "BPS" is removed to derive the base 5-character ODS code
    - The parent pharmacy (supported pharmacy type IDs) is looked up by base ODS code
        in the legacy DB
    - If a parent state record already exists, its organisation/location IDs are reused
    - If no state record exists, the parent pharmacy is migrated first (transaction 1)
        and the resulting org/location IDs are used for the BP check service (transaction 2)
    - If no parent pharmacy record exists in DoS at all, the service is rejected

    Feature flag behavior:
    - When data_migration_pharmacy_enabled is disabled:
        Service is not supported (no records created)
    - When enabled: A HealthcareService of type Blood Pressure Check is created and linked
        to the parent pharmacy organisation and location
    """

    @classmethod
    def is_service_supported(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        checks = [
            (
                is_enabled(FeatureFlag.DATA_MIGRATION_PHARMACY_ENABLED),
                "Pharmacy service selection is disabled by feature flag",
            ),
            (
                service.typeid == cls.SERVICE_TYPE_ID,
                f"Service type is not a Pharmacy type ({cls.SERVICE_TYPE_ID})",
            ),
            (
                bool(service.odscode),
                "Service does not have an ODS code",
            ),
        ]

        for condition, error_message in checks:
            if not condition:
                return False, error_message

        return cls._validate_ods_code_format(service.odscode)

    @classmethod
    def _validate_ods_code_format(cls, ods_code: str) -> tuple[bool, str | None]:
        """Validate ODS code length, suffix, and format."""
        expected_length = cls.ODS_BASE_LENGTH + len(cls.ODS_SUFFIX)

        if len(ods_code) != expected_length:
            return False, f"ODS code is not {expected_length} characters"

        if not ods_code.endswith(cls.ODS_SUFFIX):
            return False, f"ODS code does not end with {cls.ODS_SUFFIX}"

        base_ods_code = ods_code[: cls.ODS_BASE_LENGTH]

        if not cls._is_valid_pharmacy_ods_format(base_ods_code):
            return (
                False,
                "ODS code does not match required format (F + 4 alphanumeric OR alternating letter-number)",
            )

        return True, None

    @classmethod
    def _is_valid_pharmacy_ods_format(cls, base_ods_code: str) -> bool:
        """Check if base ODS code matches pharmacy format patterns."""
        return (
            BasePharmacyTransformer.PHARMACY_ODS_CODE_REGEX_F_PREFIX.match(
                base_ods_code
            )
            or BasePharmacyTransformer.PHARMACY_ODS_CODE_REGEX_ALTERNATING.match(
                base_ods_code
            )
        ) is not None

    @classmethod
    def should_include_service(
        cls,
        service: legacy_model.Service,
        state_record: "ServiceMigrationState | None" = None,
    ) -> tuple[bool, str | None]:
        should_include, reason = super().should_include_service(service, state_record)
        if not should_include:
            return False, reason

        if not service.name:
            return False, "Service name is missing"

        if not any(service.name.startswith(prefix) for prefix in cls.NAME_PREFIXES):
            return (
                False,
                "Service name does not start with required prefix (BP Check: or BP:)",
            )

        return True, None
