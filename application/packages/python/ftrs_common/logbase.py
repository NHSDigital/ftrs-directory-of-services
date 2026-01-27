from logging import DEBUG, ERROR, INFO, WARNING

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


class FeatureFlagLogBase(LogBase):
    FF_001 = LogReference(
        level=DEBUG,
        message="Initializing AppConfigStore with application_id: {application_id}, environment_id: {environment_id}, configuration_profile_id: {configuration_profile_id}, cache_ttl_seconds: {cache_ttl_seconds}",
    )
    FF_002 = LogReference(
        level=DEBUG,
        message="Feature flag '{flag_name}' evaluated to {flag_enabled} from {source}",
    )
    FF_003 = LogReference(
        level=ERROR,
        message="Failed to evaluate feature flag '{flag_name}' due to configuration store error: {exception}",
    )
    FF_004 = LogReference(
        level=ERROR,
        message="Unexpected error evaluating feature flag '{flag_name}': {exception}",
    )
