import re

from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)

from pipeline.transformer.base import ServiceTransformer, ServiceTransformOutput
from pipeline.validation.service import GPPracticeValidator


class GPProtectedLearningTimeTransformer(ServiceTransformer):
    STATUS_ACTIVE = 1
    STATUS_COMMISSIONING = 3
    SUPPORTED_TYPE_IDS = (100, 136, 159)
    ODS_CODE_REGEX = re.compile(r"^[A-Z][0-9]{5,8}$")
    VALIDATOR_CLS = GPPracticeValidator

    """
    Transformer for GP Protected Learning Time Services

    Selection criteria:
    - The service type must be 'GP Practice' (100) or 'GP Access Hub' (136) or 'Primary Care Clinic' (159)
    - The service must have an ODS code
        - 6-9 characters, beginning with a letter, and the remaining characters being numbers.
        - on import, only the first 6 characters are retained, and duplicates are removed

    Filter critiera:
    - Service status must be Active or Commissioning
    - Service name contains the following text: "PLT" OR "GP Cover"
    - Profile is linked to at least 1 SG code AND a postcode
    """

    def transform(
        self, service: legacy_model.Service, validation_issues: list[str]
    ) -> ServiceTransformOutput:
        """
        Transform the given GP Protected Learning Time Services into the new data model format

        For GP Protected Learning Time Services, Organisation Linkage is not required
        """
        organisation = self.build_organisation(service)
        location = self.build_location(service, organisation.id)
        healthcare_service = self.build_healthcare_service(
            service,
            organisation.id,
            location.id,
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.PLT_SERVICE,
            validation_issues=validation_issues,
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
        Check if the service is a GP Protected Learning Time service.
        """
        if service.typeid not in cls.SUPPORTED_TYPE_IDS:
            return False, f"Service typeid {service.typeid} is not supported"

        if not service.odscode:
            return False, "Service does not have an ODS code"

        # Check full ODS code length and format
        if not cls.ODS_CODE_REGEX.match(service.odscode):
            return False, "ODS code does not match the required format (full length)"

        # Name must contain "PLT" or "GP Cover"
        name = (service.name or "").upper()
        if "PLT" not in name and "GP COVER" not in name:
            return False, "Service name does not contain 'PLT' or 'GP Cover'"

        # Profile is linked to at least 1 SG code AND a postcode
        if not service.sgsds or not service.postcode:
            return (
                False,
                "Profile must be linked to at least 1 SG code or contain a postcode",
            )

        return True, None

    @classmethod
    def should_include_service(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        """
        Check if the service is active or commissioning.
        """
        if service.statusid not in (cls.STATUS_ACTIVE, cls.STATUS_COMMISSIONING):
            return False, "Service is not 'active' or 'commissioning'"

        return True, None
