from logging import ERROR, INFO, WARNING

from ftrs_common.logger import LogBase, LogReference


class FhirLogBase(LogBase):
    FHIR_001 = LogReference(
        level=WARNING,
        message="FHIR validation failed for resource {resource_type}: {error}",
    )


class MiddlewareLogBase(LogBase):
    MIDDLEWARE_001 = LogReference(
        level=ERROR,
        message="Error response returned with status code: {status_code}. Error message: {error_message}.",
    )
    MIDDLEWARE_002 = LogReference(
        level=INFO,
        message="Response returned with status code: {status_code}.",
    )
