import re

from ftrs_data_layer.domain import HealthcareServiceCategory, HealthcareServiceType
from ftrs_data_layer.domain import legacy as legacy_model

from pipeline.transformer.base import ServiceTransformer, ServiceTransformOutput
from pipeline.validation.service import GPPracticeValidator


class GPPracticeTransformer(ServiceTransformer):
    STATUS_ACTIVE = 1
    GP_PRACTICE_TYPE_ID = 100
    GP_PRACTICE_ODS_CODE_REGEX = re.compile(r"^[ABCDEFGHJKLMNPVWY][0-9]{5}$")
    VALIDATOR_CLS = GPPracticeValidator

    """
    Transformer for GP practice services.

    Selection criteria:
    - The service type must be 'GP Practice' (100)
    - The service must have an ODS code
    - The ODS code should be 6 characters
    - The ODS code format should start with one of the following letters: A, B, C, D, E, F, G, H, J, K, L, M, N, P, V, W, Y

    Filter criteria:
    - The service must be active

    Note on potential GP Practice misclassification:
    A SAS could be mistaken for a GP Practice if:
    - It has Typeid = 100, Status = Active, and a valid ODSCode (same format as GP Practices)
    To avoid misclassification, if the GP Practice transformer is chosen, the criteria must also:
    - Exclude orgs that match SAS filters, by excluding names with "SAS" or "Special Allocation Scheme"
    """

    def transform(
        self, service: legacy_model.Service, validation_issues: list[str]
    ) -> ServiceTransformOutput:
        """
        Transform the given GP practice service into the new data model format.
        """
        organisation = self.build_organisation(service)
        location = self.build_location(service, organisation.id)
        healthcare_service = self.build_healthcare_service(
            service,
            organisation.id,
            location.id,
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
            validation_issues=validation_issues,
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
        """
        Check if the service is a GP practice.
        """
        name = (service.name or "").upper()
        if "SAS" in name or "SPECIAL ALLOCATION SCHEME" in name:
            return False, "Service name fits GP Special Allocation Scheme criteria"

        if service.typeid != cls.GP_PRACTICE_TYPE_ID:
            return False, "Service type is not GP Practice (100)"

        if not service.odscode:
            return False, "Service does not have an ODS code"

        if not cls.GP_PRACTICE_ODS_CODE_REGEX.match(service.odscode):
            return False, "ODS code does not match the required format"

        return True, None

    @classmethod
    def should_include_service(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        """
        Check if the service is active.
        """
        if service.statusid != cls.STATUS_ACTIVE:
            return False, "Service is not active"

        return True, None
