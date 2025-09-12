import os

import boto3
import pytest
from dotenv import load_dotenv
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from loguru import logger
from pages.ui_pages.result import NewAccountPage
from pages.ui_pages.search import LoginPage
from playwright.sync_api import Page, sync_playwright
from utilities.common.file_helper import create_temp_file, delete_download_files
from utilities.infra.api_util import get_url
from utilities.infra.repo_util import model_from_json_file, check_record_in_repo
from utilities.infra.secrets_util import GetSecretWrapper
from utilities.common.constants import SERVICE_BASE_PATH
from utilities.infra.logs_util import CloudWatchLogsWrapper
import json

# Configure Loguru to log into a file and console
logger.add(
    "test_logs.log",
    rotation="1 day",
    level="INFO",
    backtrace=True,
    diagnose=True,
    mode="w",
)
logger.remove(0)

# Load base .env first
load_dotenv(".env")


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    boto3.set_stream_logger(name="botocore.credentials", level="ERROR")
    logger.info("Starting test session...")
    yield
    logger.info("Test session completed.")


@pytest.fixture(scope="session")
def playwright():
    """Start Playwright session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="module")
def api_request_context_mtls(playwright, workspace, env, api_name="servicesearch"):
    """Create a new Playwright API request context."""
    url = get_url(api_name)
    try:
        # Get mTLS certs
        client_pem_path, ca_cert_path = get_mtls_certs()
        context_options = {
            "ignore_https_errors": True,
            "client_certificates": [
                {
                    "origin": url,
                    "certPath": ca_cert_path,
                    "keyPath": client_pem_path,
                }
            ],
        }
        request_context = playwright.request.new_context(**context_options)
        yield request_context
    finally:
        try:
            delete_download_files()
        except Exception as e:
            logger.error(f"Error deleting download files: {e}")
        request_context.dispose()


# Add this fixture
@pytest.fixture(scope="module")
def cloudwatch_logs():
    """Fixture to initialize AWS CloudWatch Logs utility"""
    return CloudWatchLogsWrapper()

@pytest.fixture
def api_request_context(playwright):
    """Create a new Playwright API request context."""
    request_context = playwright.request.new_context()
    yield request_context
    request_context.dispose()

@pytest.fixture
def api_request_context_api_key(playwright, service_url: str, api_key: str):
    """Create a Playwright APIRequestContext with API key authentication."""
    context_options = {
        "base_url": service_url,
        "ignore_https_errors": True,
        "extra_http_headers": {
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json",
            "apikey": api_key,
        },
    }
    request_context = playwright.request.new_context(**context_options)
    logger.info(f"Created APIRequestContext with base_url={service_url}")
    yield request_context
    request_context.dispose()
    logger.info("Disposed APIRequestContext")

@pytest.fixture
def api_request_context_jwt(playwright, service_url: str, jwt_token: str):
    """Request context with JWT Bearer token."""
    context_options = {
        "base_url": service_url,
        "extra_http_headers": {
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json",
            "Authorization": f"Bearer {jwt_token}"
        }
    }
    request_context = playwright.request.new_context(**context_options)
    yield request_context
    request_context.dispose()

@pytest.fixture(scope="session")
def chromium():
    with sync_playwright() as p:
        chromium = p.chromium.launch()
        yield chromium
        chromium.close()


@pytest.fixture
def result_page(page: Page) -> NewAccountPage:
    return NewAccountPage(page)


@pytest.fixture
def search_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def api_response():
    """Fixture to store API response for logging in reports."""
    return {}


def _get_env_var(varname: str, default: str = None, required: bool = True) -> str:
    value = os.getenv(varname, default)
    if required:
        assert value, f"{varname} is not set"
    return value


@pytest.fixture(scope="session")
def env() -> str:
    return _get_env_var("ENVIRONMENT")


@pytest.fixture(scope="session", autouse=True)
def load_env_file(env):
    load_dotenv()


@pytest.fixture(scope="session")
def workspace() -> str:
    return _get_env_var("WORKSPACE", "", required=False)


@pytest.fixture(scope="session")
def project() -> str:
    project = _get_env_var("PROJECT_NAME", "ftrs-dos")
    return project


@pytest.fixture(scope="session")
def commit_hash() -> str:
    commit_hash = _get_env_var("COMMIT_HASH")
    return commit_hash

@pytest.fixture(scope="session")
def apigee_environment() -> str:
    return _get_env_var("APIGEE_ENVIRONMENT", default="internal-dev")


@pytest.fixture(scope="session", autouse=True)
def write_allure_environment(env, workspace, project, commit_hash):
    allure_dir = os.getenv("ALLURE_RESULTS", "allure-results")
    os.makedirs(allure_dir, exist_ok=True)
    with open(os.path.join(allure_dir, "environment.properties"), "w") as f:
        f.write(f"ENVIRONMENT={env}\n")
        f.write(f"WORKSPACE={workspace}\n")
        f.write(f"PROJECT={project}\n")
        f.write(f"COMMIT_HASH={commit_hash}\n")


@pytest.fixture(scope="session")
def organisation_repo() -> AttributeLevelRepository[Organisation]:
    return get_service_repository(Organisation, "organisation")


@pytest.fixture(scope="session")
def location_repo():
    return get_service_repository(Location, "location")


@pytest.fixture(scope="session")
def healthcare_service_repo():
    return get_service_repository(HealthcareService, "healthcare-service")


@pytest.fixture(scope="session")
def organisation_repo_seeded(organisation_repo):
    json_file = "Organisation/organisation-for-session-seeded-repo-test.json"
    organisation = model_from_json_file(json_file, organisation_repo)
    if not check_record_in_repo(organisation_repo, organisation.id):
        organisation_repo.delete(organisation.id)
    organisation_repo.create(organisation)
    yield organisation_repo
    organisation_repo.delete(organisation.id)


def get_mtls_certs():
    # Fetch secrets from AWS
    gsw = GetSecretWrapper()
    client_pem = gsw.get_secret("/temp/dev/api-ca-pk")  # Combined client cert + key
    ca_cert = gsw.get_secret("/temp/dev/api-ca-cert")  # CA cert for server verification

    # Write to temp files
    client_pem_path = create_temp_file(client_pem, ".pem")
    ca_cert_path = create_temp_file(ca_cert, ".crt")
    return client_pem_path, ca_cert_path


@pytest.fixture(scope="session")
def api_key() -> str:
    """Return the raw API key string from Secrets Manager."""
    gsw = GetSecretWrapper()
    key_json = gsw.get_secret("/ftrs-dos/dev/apim-api-key")  # returns {"api_key": "..."}
    key_dict = json.loads(key_json)
    api_key = key_dict.get("api_key")
    if not api_key:
        raise ValueError("API key not found in secret")
    logger.info(f"Fetched API key: {api_key[:4]}**** (hidden for safety)")
    return api_key

@pytest.fixture(scope="session")
def service_url(apigee_environment: str) -> str:
    """Return the base URL for API requests."""
    if apigee_environment == "prod":
        base = "https://api.service.nhs.uk"
    else:
        base = f"https://{apigee_environment}.api.service.nhs.uk"
    return f"{base.rstrip('/')}/{SERVICE_BASE_PATH}"
