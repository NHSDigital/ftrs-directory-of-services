import os
from typing import Optional

import pytest
import requests
from dotenv import load_dotenv


def get_env_var(
    var_name: str, default: Optional[str] = None, required: bool = False
) -> str:
    value = os.environ.get(var_name, default)
    if required and value is None:
        error_msg = f"Required environment variable {var_name} is not set"
        raise ValueError(error_msg)
    return value if value is not None else ""


load_dotenv()

SESSION = requests.session()

API_NAME = get_env_var("PROXYGEN_API_NAME", default="dos-ingest-api")
INSTANCE = get_env_var("INSTANCE", default="dev")
APIGEE_ENVIRONMENT = get_env_var("APIGEE_ENVIRONMENT", default="internal-dev")
NAMESPACED_API_NAME = f"{API_NAME}--{APIGEE_ENVIRONMENT}--{INSTANCE}"
SERVICE_BASE_PATH = get_env_var("SERVICE_BASE_PATH", default="dos-ingest/FHIR/R4")

os.environ["PROXY_NAME"] = NAMESPACED_API_NAME


@pytest.fixture(scope="session")
def nhsd_apim_api_name() -> str:
    """Return the API name for pytest-nhsd-apim."""
    return API_NAME


@pytest.fixture(scope="session")
def nhsd_apim_proxy_name() -> str:
    """Return the namespaced proxy name for pytest-nhsd-apim."""
    return NAMESPACED_API_NAME


@pytest.fixture(scope="session")
def api_key() -> str:
    """Return the API key from environment variables."""
    return get_env_var("API_KEY", required=True)


@pytest.fixture(scope="session")
def apigee_environment() -> str:
    """Return the Apigee environment from environment variables."""
    return APIGEE_ENVIRONMENT


@pytest.fixture(scope="session")
def service_url(apigee_environment: str) -> str:
    if apigee_environment == "prod":
        base_url = "https://api.service.nhs.uk"
    else:
        base_url = f"https://{apigee_environment}.api.service.nhs.uk"

    return f"{base_url}/{SERVICE_BASE_PATH}"


@pytest.fixture(scope="session")
def base_headers() -> dict[str, str]:
    """Return the base headers for all requests."""
    return {"Content-Type": "application/fhir+json", "Accept": "application/fhir+json"}
