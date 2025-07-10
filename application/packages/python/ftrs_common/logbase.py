from logging import WARNING

from ftrs_common.logger import LogBase, LogReference


class FhirLogBase(LogBase):
    FHIR_001 = LogReference(
        level=WARNING,
        message="FHIR validation failed for resource {resource_type}: {error}",
    )
