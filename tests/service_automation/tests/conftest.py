import pytest
import os
import boto3
from dotenv import load_dotenv
from loguru import logger
from playwright.sync_api import sync_playwright, Page, APIRequestContext
from utilities.infra.secrets_util import GetSecretWrapper
from utilities.common.file_helper import create_temp_file
from utilities.infra.api_util import get_r53
from pages.ui_pages.search import LoginPage
from pages.ui_pages.result import NewAccountPage


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


@pytest.fixture
def api_request_context(playwright, workspace, env, api_name = "servicesearch"):
    """Create a new Playwright API request context."""
    r53 = get_r53(workspace, api_name, env)
    # Get mTLS certs
    client_pem_path, ca_cert_path = get_mtls_certs()
    context_options = {
        "ignore_https_errors": True,
        "client_certificates": [
            {
                "origin": f"https://{r53}",
                "certPath": ca_cert_path,
                "keyPath": client_pem_path,
            }
        ]
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


def _get_env_var(varname: str) -> str:
    value = os.getenv(varname)
    assert value, f"{varname} is not set"
    return value


@pytest.fixture(scope="session")
def env() -> str:
    return _get_env_var("ENVIRONMENT")


@pytest.fixture(scope="session", autouse=True)
def load_env_file(env):
    load_dotenv(f".env.{env}", override=True)


@pytest.fixture(scope="session")
def workspace() -> str:
    return _get_env_var("WORKSPACE")


@pytest.fixture(scope="session")
def project() -> str:
    project = _get_env_var("project")
    return project


@pytest.fixture(scope="session")
def commit_hash() -> str:
    commit_hash = _get_env_var("COMMIT_HASH")
    return commit_hash


@pytest.fixture(scope="session", autouse=True)
def write_allure_environment(env, workspace, project, commit_hash):
    allure_dir = os.getenv("ALLURE_RESULTS", "allure-results")
    os.makedirs(allure_dir, exist_ok=True)
    with open(os.path.join(allure_dir, "environment.properties"), "w") as f:
        f.write(f"ENVIRONMENT={env}\n")
        f.write(f"WORKSPACE={workspace}\n")
        f.write(f"PROJECT={project}\n")
        f.write(f"COMMIT_HASH={commit_hash}\n")


def get_mtls_certs():
    # Fetch secrets from AWS
    gsw = GetSecretWrapper()
    client_pem = gsw.get_secret('/temp/dev/api-ca-pk')       # Combined client cert + key
    ca_cert = gsw.get_secret('/temp/dev/api-ca-cert')        # CA cert for server verification

    # Write to temp files
    client_pem_path = create_temp_file(client_pem, '.pem')
    ca_cert_path = create_temp_file(ca_cert, '.crt')
    return client_pem_path, ca_cert_path
