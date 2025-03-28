import pytest
import os
from loguru import logger
from playwright.sync_api import sync_playwright
import pytest_html


# Configure Loguru to log into a file and console
logger.add("test_logs.log", rotation="1 day", level="INFO", backtrace=True, diagnose=True)

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
    if _get_env_var('WORKSPACE') != "default":
        workspace = _get_env_var('WORKSPACE')
    else:
        workspace = ""
    return workspace

@pytest.fixture(scope='session')
def env() -> str:
    return _get_env_var('ENV')


def pytest_html_report_title(report):
    """Set custom title for pytest HTML report."""
    report.title = "Playwright API Test Report"


@pytest.hookimpl(tryfirst=True)
def pytest_html_results_table_header(cells):
    """Modify table headers in HTML report to include API logs."""
    cells.insert(2, "Request")
    cells.insert(3, "Response Status")
    cells.insert(4, "Response Body")
    cells.insert(5, "Assertion Message")


@pytest.hookimpl(tryfirst=True)
def pytest_html_results_table_row(report, cells):
    """Add API logs to each test result row."""
    if hasattr(report, "extra_info"):
        cells.insert(2, report.extra_info.get("request", "N/A"))
        cells.insert(3, report.extra_info.get("response_status", "N/A"))
        cells.insert(4, report.extra_info.get("response_body", "N/A"))
        cells.insert(5, report.extra_info.get("success_message", "N/A"))


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Attach API logs to pytest reports."""
    if "api_response" in item.funcargs:
        api_response = item.funcargs["api_response"]
        request = api_response.get("request", "N/A")
        response_status = api_response.get("response_status", "N/A")
        response_body = api_response.get("response_body", "N/A")
        success_message = api_response.get("success_message", "N/A")

        extra_info = getattr(item, "extra_info", {})
        extra_info.update({
            "request": request,
            "response_status": response_status,
            "response_body": response_body,
            "success_message": success_message,
        })
        item.extra_info = extra_info

        #  Attach API logs to the HTML report
        if hasattr(item.config, "_html") and hasattr(item.config._html, "extras"):
            item.config._html.extras.append(pytest_html.extras.text(f"Request: {request}"))
            item.config._html.extras.append(pytest_html.extras.text(f"Response Status: {response_status}"))
            item.config._html.extras.append(pytest_html.extras.text(f"Response Body: {response_body}"))
            item.config._html.extras.append(pytest_html.extras.text(f"Assertion Message: {success_message}"))
