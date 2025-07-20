
import pytest
import allure
from pages.ui_pages.rov_home import HomePage
from pages.ui_pages.rov_organisations import OrganisationsPage
from playwright.sync_api import sync_playwright, expect, Page
from utilities.infra.cloudfront_util import CloudFrontWrapper
from utilities.common.resource_name import get_resource_name
from loguru import logger

@pytest.fixture(scope="module")
def api_request_context():
    """Initialize Playwright APIRequestContext"""
    with sync_playwright() as p:
        request_context = p.request.new_context()
        yield request_context
        request_context.dispose()


def get_cloudfront(workspace, project, env):
    cloudfront_s3 = get_resource_name(project, workspace, env, "read-only-viewer", "frontend-bucket")
    logger.info(f"CloudFront S3 Bucket: {cloudfront_s3}")
    cfw = CloudFrontWrapper()
    cloudfront_url = cfw.list_distributions(cloudfront_s3)
    logger.info(f"CloudFront Distributions: {cloudfront_url}")
    return cloudfront_url


@allure.id(1)
@allure.story("Read only viewer tests")
@allure.title("Test to loading the home page")
@pytest.mark.ui
def test_loading_home_page( page: Page,
    home_page: HomePage, workspace, project, env) -> None:
    cloudfront_url = get_cloudfront(workspace, project, env)
    # Given the read only viewer home page is displayed
    logger.info(f"Loading home page: {cloudfront_url}")
    with allure.step("Given the home page is displayed"):
        home_page.load(cloudfront_url)

    # Then the page title is displayed
    with allure.step("Then Read Only viewer is displayed"):
        expect(home_page.heading).to_be_visible()

    # Then the Oranisation link is displayed
    with allure.step("Then link to Organisation is displayed"):
        expect(home_page.Organisations_link).to_be_visible()
        page.screenshot(path="allure-results/screenshot.png")


@allure.id(1)
@allure.story("Read only viewer tests")
@allure.title("Test to loading the organisations page")
@pytest.mark.ui
def test_loading_organisations_page( page: Page,
    home_page: HomePage, organisation_page: OrganisationsPage, workspace, project, env) -> None:
    cloudfront_url = get_cloudfront(workspace, project, env)

    with allure.step("Given the home page is displayed"):
        home_page.load(cloudfront_url)

    # When the organizations link is clicked
    with allure.step("When the organizations link is clicked"):
        home_page.Organisations_link.click()

    # Then the Organizations page is displayed
    with allure.step("Then the Organizations page is displayed"):
        expect(organisation_page.heading).to_be_visible()
