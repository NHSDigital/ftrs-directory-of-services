"""
These tests cover sample ui requests.
"""
import pytest
from pages.ui_pages.result import UserTestMfaHelpPage
from pages.ui_pages.search import UserTestLoginPage
from playwright.sync_api import sync_playwright, expect, Page

@pytest.fixture(scope="session")
def api_request_context():
    """Initialize Playwright APIRequestContext"""
    with sync_playwright() as p:
        request_context = p.request.new_context()
        yield request_context
        request_context.dispose()


def test_basic_ui_search(
    page: Page,
    search_page: UserTestLoginPage,
    result_page: UserTestMfaHelpPage) -> None:

    # Given the UserTest home page is displayed
    search_page.load()

    # When the MFA help link is clicked
    search_page.search()

    # Then the helptest is displayed
    expect(result_page.page.get_by_text("How you log into DoS is changing")).to_be_visible
