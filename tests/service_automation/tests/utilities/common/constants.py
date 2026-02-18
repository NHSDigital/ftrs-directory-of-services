ODS_TERMINOLOGY_INT_API_URL = (
    "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
)
ENDPOINTS = {
    "health": "/_ping",
    "status": "/_status",
    "organization": "/Organization",
}

"""Constants and configuration for data migration tests."""

# Fields that should always remain as strings even if they look like numbers
STRING_FIELDS = frozenset(
    {
        "uid",
        "publicphone",
        "web",
        "email",
        "address",
        "postcode",
        "fax",
        "nonpublicphone",
    }
)

# Fields that contain datetime values
DATETIME_FIELDS = frozenset(
    {
        "createdtime",
        "modifiedtime",
        "lastupdated",
        "effectivedate",
    }
)

# Boolean fields
BOOLEAN_FIELDS = frozenset(
    {
        "openallhours",
        "restricttoreferrals",
        "active",
        "isactive",
    }
)

# DynamoDB Configuration
DYNAMODB_CLIENT = "client"
DYNAMODB_RESOURCE = "resource"
DYNAMODB_ENDPOINT = "endpoint_url"

# Maps entity type names used in BDD scenarios to their corresponding
# field names in the DynamoDB state table record
STATE_TABLE_ENTITY_ID_FIELDS = {
    "organisation": "organisation_id",
    "location": "location_id",
    "healthcare_service": "healthcare_service_id",
}

# Environment Variables
ENV_PROJECT_NAME = "PROJECT_NAME"
ENV_ENVIRONMENT = "ENVIRONMENT"
ENV_WORKSPACE = "WORKSPACE"

# Database Configuration
PATHWAYSDOS_SCHEMA = "pathwaysdos"
SERVICES_TABLE = f"{PATHWAYSDOS_SCHEMA}.services"
SERVICETYPES_TABLE = f"{PATHWAYSDOS_SCHEMA}.servicetypes"

# Validation
REQUIRED_SERVICE_FIELDS: list[str] = ["id", "typeid", "statusid"]

# DynamoDB Resources
EXPECTED_DYNAMODB_RESOURCES: list[tuple[str, str]] = [
    ("database", "organisation"),
    ("database", "location"),
    ("database", "healthcare-service"),
    ("data-migration", "state"),
]

# Version History Configuration
VERSION_HISTORY_TRACKED_ENTITIES = frozenset(
    {
        "organisation",
        "location",
        "healthcare-service",
    }
)

VERSION_HISTORY_CHANGE_TYPES = frozenset(
    {
        "UPDATE",
        "CREATE",
        "DELETE",
    }
)

VERSION_HISTORY_CHANGED_BY_TYPES = frozenset(
    {
        "app",
        "user",
        "system",
    }
)

# Default stream processing wait time (seconds)
STREAM_PROCESSING_WAIT_TIME = 3
STREAM_INITIAL_SETTLE_TIME = 2

# Maximum age in seconds for version history timestamp validation
VERSION_HISTORY_MAX_AGE_SECONDS = 10
