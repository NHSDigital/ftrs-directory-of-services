import pytest
import os
from config import config
from loguru import logger
from playwright.sync_api import sync_playwright, Page, APIRequestContext
from pages.ui_pages.search import UserTestLoginPage
from pages.ui_pages.result import UserTestMfaHelpPage


# Configure Loguru to log into a file and console
logger.add("test_logs.log", rotation="1 day", level="INFO", backtrace=True, diagnose=True, mode="w")
logger.remove(0)

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
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


@pytest.fixture(scope='session')
def chromium():
    with sync_playwright() as p:
        chromium = p.chromium.launch()
        yield chromium
        chromium.close()

@pytest.fixture
def result_page(page: Page) -> UserTestMfaHelpPage:
    return UserTestMfaHelpPage(page)

@pytest.fixture
def search_page(page: Page) -> UserTestLoginPage:
    return UserTestLoginPage(page)


@pytest.fixture
def api_response():
    """Fixture to store API response for logging in reports."""
    return {}


def _get_env_var(varname: str) -> str:
    value = os.getenv(varname)
    assert value, f'{varname} is not set'
    return value

@pytest.fixture(scope='session')
def workspace() -> str:
    if config.get("workspace") != "default":
        workspace = config.get("workspace")
    else:
        workspace = ""
    return workspace


@pytest.fixture(scope='session')
def env() -> str:
    env = config.get_environment()
    return env


@pytest.fixture(scope='session')
def project() -> str:
    project = config.get("project")
    return project
