import re

from ftrs_data_layer.domain import HealthcareServiceCategory, HealthcareServiceType
from ftrs_data_layer.domain.legacy.data_models import ServiceData

from service_migration.models import TransformResult
from service_migration.transformer.base import ServiceTransformer
from service_migration.validation.service import GPPracticeValidator


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
    """

    def transform(self, service: ServiceData) -> TransformResult:
        """
        Transform the given GP practice service into the new data model format.
        """
        organisation = self.mappers.organisation.map(service)
        location = self.mappers.location.map(service, organisation.id)
        healthcare_service = self.mappers.healthcare_service.map(
            service,
            organisation.id,
            location.id,
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
        )

        return TransformResult(
            organisation=organisation,
            healthcare_service=healthcare_service,
            location=location,
        )

    @classmethod
    def is_service_supported(cls, service: ServiceData) -> tuple[bool, str | None]:
        """
        Check if the service is a GP practice.
        """
        if service.typeid != cls.GP_PRACTICE_TYPE_ID:
            return False, "Service type is not GP Practice (100)"

        if not service.odscode:
            return False, "Service does not have an ODS code"

        if not cls.GP_PRACTICE_ODS_CODE_REGEX.match(service.odscode):
            return False, "ODS code does not match the required format"

        return True, None

    @classmethod
    def should_include_service(cls, service: ServiceData) -> tuple[bool, str | None]:
        """
        Check if the service is active.
        """
        if service.statusid != cls.STATUS_ACTIVE:
            return False, "Service is not active"

        return True, None
