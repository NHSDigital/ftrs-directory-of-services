import os

import boto3
import pytest
from dotenv import load_dotenv
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.models import HealthcareService, Location, Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from loguru import logger
from pages.ui_pages.result import NewAccountPage
from pages.ui_pages.search import LoginPage
from playwright.sync_api import Page, sync_playwright
from utilities.infra.repo_util import model_from_json_file

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
def api_request_context(playwright):
    """Create a new Playwright API request context."""
    request_context = playwright.request.new_context()
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
    load_dotenv()


@pytest.fixture(scope="session")
def workspace() -> str:
    return _get_env_var("WORKSPACE")


@pytest.fixture(scope="session")
def project() -> str:
    project = _get_env_var("PROJECT_NAME")
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
    json_file = "Organisation/00000000-bab3-4baf-92da-0c77df9363a6.json"
    organisation = model_from_json_file(json_file, organisation_repo)
    organisation_repo.create(organisation)
    yield organisation_repo
    organisation_repo.delete(organisation.id)
