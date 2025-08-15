import re

from ftrs_data_layer.domain import legacy as legacy_model

from pipeline.transformer.base import ServiceTransformer


class GPProtectedLearningTimeTransformer(ServiceTransformer):
    STATUS_ACTIVE = 1
    STATUS_COMMISSIONING = 3
    SUPPORTED_TYPE_IDS = (100, 136, 159)
    ODS_CODE_REGEX = re.compile(r"^[A-Z][0-9]{5,8}$")

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

        # Profile must contain a postcode
        if not service.postcode:
            return False, "Profile must contain a postcode"

        return True, None

    @classmethod
    def should_include_service(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        """
        Check if the service is active and commissioning.
        """
        if service.statusid != cls.STATUS_ACTIVE:
            return False, "Service is not active"

        if service.statusid != cls.STATUS_COMMISSIONING:
            return False, "Service is not commissioning"

        return True, None
