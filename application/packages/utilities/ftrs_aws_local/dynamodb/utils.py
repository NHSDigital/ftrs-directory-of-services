from enum import StrEnum

MISSING_PARAMETERS = "entity_type and env parameters are required"


class TargetEnvironment(StrEnum):
    local = "local"
    dev = "dev"


class ClearableEntityTypes(StrEnum):
    organisation = "organisation"
    healthcare_service = "healthcare-service"
    location = "location"
    triage_code = "triage-code"
    state = "state"


DEFAULT_CLEARABLE_ENTITY_TYPES = [
    ClearableEntityTypes.organisation,
    ClearableEntityTypes.healthcare_service,
    ClearableEntityTypes.location,
    ClearableEntityTypes.triage_code,
    ClearableEntityTypes.state,
]
