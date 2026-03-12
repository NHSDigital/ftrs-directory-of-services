from typing import TYPE_CHECKING

from ftrs_common.feature_flags import FeatureFlag, is_enabled
from ftrs_data_layer.domain import HealthcareServiceType
from ftrs_data_layer.domain import legacy as legacy_model

from service_migration.transformer.base_pharmacy import LinkedPharmacyTransformer

if TYPE_CHECKING:
    from service_migration.models import ServiceMigrationState


class PharmacyFirstTransformer(LinkedPharmacyTransformer):
    STATUS_ACTIVE = 1
    SERVICE_TYPE_ID = 132
    ODS_SUFFIXES = (
        "M06DSP",
        "M06",
    )
    NAME_PREFIX = "PF++:"
    HEALTHCARE_SERVICE_TYPE = HealthcareServiceType.PHARMACY_FIRST

    """
    Transformer for Pharmacy First services.

    Selection criteria:
    - The service type must be 'Pharmacy Enhanced' (132)
    - The service must have an ODS code ending with 'M06' or 'M06DSP'
    - The service name must be prefixed with 'PF++:'

    Filter criteria:
    - The service must be active

    Parent pharmacy resolution:
    - The ODS suffix ('M06' or 'M06DSP') is removed to derive the base ODS code
    - The parent pharmacy (type 13 or 134) is looked up by base ODS code in the legacy DB
    - If a parent state record already exists, its organisation/location IDs are reused
    - If no state record exists, the parent pharmacy is migrated first (transaction 1)
      and the resulting org/location IDs are used for the pharmacy first service (transaction 2)
    - If no parent pharmacy record exists in DoS at all, the service is rejected

    Feature flag behavior:
    - When data_migration_pharmacy_enabled is disabled:
      Service is not supported (no records created)
    - When enabled: A HealthcareService of type Pharmacy First is created and linked
      to the parent pharmacy organisation and location
    """

    def derive_base_ods_code(self, service: legacy_model.Service) -> str:
        ods_code = service.odscode
        for suffix in self.ODS_SUFFIXES:
            if ods_code.endswith(suffix):
                return ods_code.removesuffix(suffix)

        raise ValueError(f"ODS code does not end with expected suffixes: {ods_code}")

    @classmethod
    def is_service_supported(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        if not is_enabled(FeatureFlag.DATA_MIGRATION_PHARMACY_ENABLED):
            return (
                False,
                "Pharmacy First service selection is disabled by feature flag",
            )

        if service.typeid != cls.SERVICE_TYPE_ID:
            return (
                False,
                f"Service type is not a Pharmacy First type ({cls.SERVICE_TYPE_ID})",
            )

        if not service.odscode:
            return False, "Service does not have an ODS code"

        # Check if ODS code ends with any of the expected suffixes
        if not any(service.odscode.endswith(suffix) for suffix in cls.ODS_SUFFIXES):
            return (
                False,
                f"ODS code does not end with required suffixes ({', '.join(cls.ODS_SUFFIXES)})",
            )

        if not service.name or not service.name.startswith(cls.NAME_PREFIX):
            return (
                False,
                f"Service name does not start with the required prefix ({cls.NAME_PREFIX!r})",
            )

        return True, None

    @classmethod
    def should_include_service(
        cls,
        service: legacy_model.Service,
        state_record: "ServiceMigrationState | None" = None,
    ) -> tuple[bool, str | None]:
        return super().should_include_service(service, state_record)
