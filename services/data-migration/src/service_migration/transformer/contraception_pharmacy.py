from ftrs_common.feature_flags import FeatureFlag, is_enabled
from ftrs_data_layer.domain import HealthcareServiceType
from ftrs_data_layer.domain import legacy as legacy_model

from service_migration.transformer.base_pharmacy import LinkedPharmacyTransformer


class ContraceptionPharmacyTransformer(LinkedPharmacyTransformer):
    STATUS_ACTIVE = 1
    CONTRACEPTION_TYPE_ID = 149
    ODS_SUFFIX = "CON"
    CON_NAME_PREFIX = "Contraception: "
    HEALTHCARE_SERVICE_TYPE = (
        HealthcareServiceType.ORAL_CONTRACEPTION_PRESCRIPTION_AND_SUPPLY
    )

    """
    Transformer for Contraception pharmacy services.

    Selection criteria:
    - The service type must be 'Pharmacy Contraception' (149)
    - The service must have an ODS code ending with 'CON'
    - The service name must be prefixed with 'Contraception: '

    Filter criteria:
    - The service must be active

    Parent pharmacy resolution:
    - The ODS suffix 'CON' is removed to derive the base ODS code (no length validation)
    - The parent pharmacy (type 13 or 134) is looked up by base ODS code in the legacy DB
    - If a parent state record already exists, its organisation/location IDs are reused
    - If no state record exists, the parent pharmacy is migrated first (transaction 1)
      and the resulting org/location IDs are used for the contraception service (transaction 2)
    - If no parent pharmacy record exists in DoS at all, the service is rejected

    Feature flag behavior:
    - When data_migration_pharmacy_enabled is disabled:
      Service is not supported (no records created)
    - When enabled: A HealthcareService of type Oral Contraception Prescription and Supply
      is created and linked to the parent pharmacy organisation and location
    """

    @classmethod
    def is_service_supported(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        if not is_enabled(FeatureFlag.DATA_MIGRATION_PHARMACY_ENABLED):
            return (
                False,
                "Contraception pharmacy service selection is disabled by feature flag",
            )

        if service.typeid != cls.CONTRACEPTION_TYPE_ID:
            return (
                False,
                f"Service type is not a Contraception Pharmacy type ({cls.CONTRACEPTION_TYPE_ID})",
            )

        if not service.odscode:
            return False, "Service does not have an ODS code"

        if not service.odscode.endswith(cls.ODS_SUFFIX):
            return (
                False,
                f"ODS code does not end with the required suffix ({cls.ODS_SUFFIX})",
            )

        if not service.name or not service.name.startswith(cls.CON_NAME_PREFIX):
            return (
                False,
                f"Service name does not start with the required prefix ({cls.CON_NAME_PREFIX!r})",
            )

        return True, None
