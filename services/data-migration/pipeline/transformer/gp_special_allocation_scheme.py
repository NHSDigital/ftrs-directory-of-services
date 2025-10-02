import re

from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)

from pipeline.transformer.base import ServiceTransformer, ServiceTransformOutput
from pipeline.validation.service import GPPracticeValidator


class GPSpecialAllocationSchemeTransformer(ServiceTransformer):
    STATUS_ACTIVE = 1
    SUPPORTED_TYPE_ID = 100
    ODS_CODE_REGEX = re.compile(r"^[A-Z][0-9]{5}$")  # 6 characters: 1 letter + 5 digits
    VALIDATOR_CLS = GPPracticeValidator

    """
    Transformer for GP Special Allocation Scheme Services

    Selection criteria:
    - The service type must be 'GP Practice' (100)
    - The service must have an ODS code
        - 6 characters, beginning with a letter, and the remaining characters being numbers

    Filter critiera:
    - Service status must be Active
    - Service name contains the following text: "SAS" OR "Special Allocation Scheme"
    """

    def transform(
        self, service: legacy_model.Service, validation_issues: list[str]
    ) -> ServiceTransformOutput:
        """
        Transform the given GP Special Allocation Scheme Service into the new data model format

        For GP Special Allocation Scheme Services, Organisation Linkage is not required
        Creates only the healthcare service without organisation and location entities
        """
        organisation = self.build_organisation(service)
        location = self.build_location(service, organisation.id)
        healthcare_service = self.build_healthcare_service(
            service,
            organisation.id,
            location.id,
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.SAS_SERVICE,
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
        Check if the service is a GP Special Allocation Scheme Service
        """
        if service.typeid != cls.SUPPORTED_TYPE_ID:
            return False, f"Service typeid {service.typeid} is not supported"

        if not service.odscode:
            return False, "Service does not have an ODS code"

        # Check full ODS code length and format
        if not cls.ODS_CODE_REGEX.match(service.odscode):
            return (
                False,
                "ODS code does not match the required format (6 chars, 1 letter + 5 digits)",
            )

        # Name must contain "SAS" or "Special Allocation Scheme"
        name = (service.name or "").upper()
        if "SAS" not in name and "SPECIAL ALLOCATION SCHEME" not in name:
            return (
                False,
                "Service name does not contain 'SAS' or 'Special Allocation Scheme'",
            )

        return True, None

    @classmethod
    def should_include_service(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        """
        Check if the service is active.
        """
        if service.statusid != cls.STATUS_ACTIVE:
            return False, "Service is not 'active'"

        return True, None
