import re

from ftrs_data_layer.domain import legacy as legacy_model

from pipeline.transformer.base import ServiceTransformer


class GPSpecialAllocationSchemeTransformer(ServiceTransformer):
    STATUS_ACTIVE = 1
    SUPPORTED_TYPE_ID = 100
    ODS_CODE_REGEX = re.compile(r"^[A-Z][0-9]{5}$")  # 6 characters: 1 letter + 5 digits

    @classmethod
    def is_service_supported(
        cls, service: legacy_model.Service
    ) -> tuple[bool, str | None]:
        """
        Check if the service is a GP Special Allocation Scheme service.
        """
        if service.typeid != cls.SUPPORTED_TYPE_ID:
            return False, f"Service typeid {service.typeid} is not supported"

        if not service.odscode:
            return False, "Service does not have an ODS code"

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
            return False, "Service is not active"

        return True, None
