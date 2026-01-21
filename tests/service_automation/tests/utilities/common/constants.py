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
