ODS_TERMINOLOGY_INT_API_URL = (
    "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
)
ENDPOINTS = {
    "health": "/_ping",
    "status": "/_status",
    "organization": "/Organization",
}

"""Constants for BDD test data manipulation."""

# Fields that should always remain as strings even if they look like numbers
STRING_FIELDS = frozenset({
    "uid",
    "publicphone",
    "web",
    "email",
    "address",
    "postcode",
    "fax",
    "nonpublicphone",
})

# Fields that contain datetime values
DATETIME_FIELDS = frozenset({
    "createdtime",
    "modifiedtime",
    "lastupdated",
    "effectivedate",
})

# Boolean fields
BOOLEAN_FIELDS = frozenset({
    "openallhours",
    "restricttoreferrals",
    "active",
    "isactive",
})
