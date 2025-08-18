import re

from ftrs_data_layer.domain import HealthcareServiceCategory, HealthcareServiceType
from ftrs_data_layer.domain import legacy as legacy_model

from pipeline.transformer.base import ServiceTransformer, ServiceTransformOutput


class GPEnhancedAccessTransformer(ServiceTransformer):
    STATUS_ACTIVE = 1
    GP_ACCESS_HUB_TYPE_ID = 136
    PCN_ENHANCED_SERVICE_TYPE_ID = 152
    GP_ENHANCED_ACCESS_ODS_CODE_REGEX = re.compile(r"^U\d{5}$")

    # Name exclusion patterns
    EXCLUDED_NAME_PATTERNS = [
        "GP Protected Learning Time (PLT)",
        "ARI - ",
        "Primary Care CAS - ",
    ]

    """
    Transformer for GP Enhanced Access services

    Selection criteria:
    - The service type must be 'GP Access Hub' (136) or 'Primary Care Network (PCN) Enhanced Service' (152)
    - The service must have an ODS code
    - Only the first 6 characters of the ODS code are retained
    - The ODS code format should match (Unnnnn) - beginning with letter 'U' followed by 5 digits

    Filter criteria:
    - The service must be active
    - Service name must not contain excluded patterns: "GP Protected Learning Time (PLT)", "ARI - ", "Primary Care CAS - "
    """

    def transform(self, service: legacy_model.Service) -> ServiceTransformOutput:
        """
        Transform the given GP Enhanced Access service into the new data model format.

        For GP Enhanced Access services, organisation linkage is not required
        Create only the healthcare service without organisation and location entities
        """
        healthcare_service = self.build_healthcare_service(
            service,
            None,
            None,
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.PCN_SERVICE,
        )

        return ServiceTransformOutput(
            organisation=[],
            healthcare_service=[healthcare_service],
            location=[],
        )

    @classmethod
    def is_service_supported(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        """
        Check if the service is a GP Enhanced Access service.
        """
        if service.typeid not in [
            cls.GP_ACCESS_HUB_TYPE_ID,
            cls.PCN_ENHANCED_SERVICE_TYPE_ID,
        ]:
            return (
                False,
                "Service type is not GP Access Hub (136) or Primary Care Network (PCN) Enhanced Service (152)",
            )

        if not service.odscode:
            return False, "Service does not have an ODS code"

        # Retain only the first 6 characters of ODS code for validation
        truncated_ods_code = service.odscode[:6]

        if not cls.GP_ENHANCED_ACCESS_ODS_CODE_REGEX.match(truncated_ods_code):
            return (
                False,
                "ODS code (first 6 characters) does not match the required format (Unnnnn)",
            )

        return True, None

    @classmethod
    def should_include_service(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        """
        Check if the service should be included based on status and name criteria.
        """
        if service.statusid != cls.STATUS_ACTIVE:
            return False, "Service is not active"

        # Check if service name contains any excluded patterns
        if service.name:
            for excluded_pattern in cls.EXCLUDED_NAME_PATTERNS:
                if excluded_pattern in service.name:
                    return (
                        False,
                        f"Service name contains excluded pattern: '{excluded_pattern}'",
                    )

        return True, None
