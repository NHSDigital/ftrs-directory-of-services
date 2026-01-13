"""URL utilities for building API endpoints."""

import os
from functools import cache

# Constants specific to URL building
ENV_LOCAL = "local"
ENV_ENVIRONMENT = "ENVIRONMENT"
ENV_LOCAL_APIM_API_URL = "LOCAL_APIM_API_URL"
ENV_APIM_URL = "APIM_URL"
ENV_LOCAL_ODS_URL = "LOCAL_ODS_URL"
ENV_ODS_URL = "ODS_URL"
DEFAULT_ODS_URL = (
    "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
)


@cache
def get_base_apim_api_url() -> str:
    """Get the base APIM API URL based on environment."""
    env = os.environ.get(ENV_ENVIRONMENT, ENV_LOCAL)

    if env == ENV_LOCAL:
        return os.environ[ENV_LOCAL_APIM_API_URL]

    return os.environ.get(ENV_APIM_URL)


@cache
def get_base_ods_terminology_api_url() -> str:
    """Get the base ODS Terminology API URL based on environment."""
    env = os.environ.get(ENV_ENVIRONMENT, ENV_LOCAL)

    if env == ENV_LOCAL:
        return os.environ.get(ENV_LOCAL_ODS_URL, DEFAULT_ODS_URL)

    ods_url = os.environ.get(ENV_ODS_URL)
    if ods_url is None:
        err_msg = f"{ENV_ODS_URL} environment variable is not set"
        raise KeyError(err_msg)
    return ods_url


def build_organization_search_url(base_url: str, identifier: str) -> str:
    identifier_param = f"odsOrganisationCode|{identifier}"
    return f"{base_url}/Organization?identifier={identifier_param}"


def build_organization_update_url(base_url: str, org_uuid: str) -> str:
    return f"{base_url}/Organization/{org_uuid}"
