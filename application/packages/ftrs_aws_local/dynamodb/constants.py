from enum import StrEnum


class ClearableEntityType(StrEnum):
    organisation = "organisation"
    healthcare_service = "healthcare-service"
    location = "location"
    triage_code = "triage-code"
    state = "data-migration-state"


class RepositoryTypes(StrEnum):
    document = "document"
    field = "field"


ALL_ENTITY_TYPES = [
    ClearableEntityType.organisation,
    ClearableEntityType.healthcare_service,
    ClearableEntityType.location,
    ClearableEntityType.triage_code,
    ClearableEntityType.state,
]


class TargetEnvironment(StrEnum):
    local = "local"
    dev = "dev"
