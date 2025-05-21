"""
These tests cover sample ui requests.
"""
import pytest
import allure
from pages.ui_pages.result import NewAccountPage
from pages.ui_pages.search import LoginPage
from playwright.sync_api import sync_playwright, expect, Page

@pytest.fixture(scope="session")
def api_request_context():
    """Initialize Playwright APIRequestContext"""
    with sync_playwright() as p:
        request_context = p.request.new_context()
        yield request_context
        request_context.dispose()

@allure.id(1)
@allure.story("Sample UI Tests")
@allure.title("Test to demonstrate accessing a web page")
@pytest.mark.ui
def test_basic_ui_search(
    page: Page,
    search_page: LoginPage,
    result_page: NewAccountPage) -> None:

    # Given the UserTest home page is displayed
    with allure.step("Given the home page is displayed"):
        search_page.load()

    # When the new account link is clicked
    with allure.step("When the request new account link is clicked"):
        search_page.search()

    # Then the Request account form is displayed
    with allure.step("Then  Request account is displayed"):
        expect(result_page.page.get_by_text("Request account")).to_be_visible
