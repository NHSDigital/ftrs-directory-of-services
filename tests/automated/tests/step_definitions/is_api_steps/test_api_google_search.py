import pytest
import json
from loguru import logger
from pytest_bdd import given, when, then, scenarios
from playwright.sync_api import sync_playwright
from config import config  # Ensure Config is correctly imported

# Load feature file
scenarios("./is_api_features/test_api_google_search.feature")

# @pytest.fixture(scope="session")
# def api_request_context():
#     """Initialize Playwright APIRequestContext"""
#     with sync_playwright() as p:
#         request_context = p.request.new_context()
#         yield request_context
#         request_context.dispose()

@pytest.fixture
def api_response():
    """Fixture to store API response for logging in reports."""
    return {}

@given("I make GET request to the Google search API")
def prepare_google_search_request(api_response):
    """Step to prepare Google API details from the config file and set the request parameters."""

    # Retrieve API details directly from the config
    base_url = config.get("base_url")
    api_key = config.get("api_key")
    search_engine_id = config.get("search_engine_id")

    # Prepare params for the API request
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": "Playwright"
    }

    # Store request for logging
    api_response["base_url"] = base_url
    api_response["params"] = params
    api_response["request"] = json.dumps(params, indent=2)
    logger.info("api response", api_response)

@when("I receive the response")
def make_google_search_request(api_request_context, api_response):
    """Make the GET request using the parameters prepared in the @given step"""

    # Use the parameters prepared in the @given step
    base_url = api_response.get("base_url")
    params = api_response.get("params")

    logger.info("base url:", base_url)

    # Make the GET request (using Playwright's APIRequestContext)
    response = api_request_context.get(base_url, params=params)
    logger.info("response:", response)


    # Store response status and body for logging
    api_response["response_status"] = response.status
    try:
        response_json = response.json()
        api_response["response_body"] = json.dumps(response_json, indent=2)
        logger.info("response:", api_response["response_body"])
    except Exception as e:
        pytest.fail(f"Invalid JSON response: {e}")
        logger.info("Invalid JSON:", e)
        return

    # Print request & response in log
    logger.info(f"--- API Request ---: {json.dumps(params, indent=2)}")
    logger.info(f"Status Code: {response.status}")
    logger.info(f"--- API Response ---: {json.dumps(response_json, indent=2)}")

    # Store the response for validation in the @then step
    api_response["response_json"] = response_json

@then("I should see search results")
def verify_response_and_search_results(api_response):
    """Verify the response status and search results contain 'Playwright'"""
    response_json = api_response.get("response_json", {})
    # Ensure response is valid
    assert api_response["response_status"] == 200, \
        f"Unexpected status code: {api_response['response_status']}"
    # Assert that 'title' matches the expected value
    assert response_json.get("queries", {}).get("request", [{}])[0].get("title") == "Google Custom Search - Playwright", \
        f"Expected 'title' to be 'Google Custom Search - Playwright', but got {response_json.get('queries', {}).get('request', [{}])[0].get('title')}"

    # Assert that 'searchTerms' matches the expected value
    assert response_json.get("queries", {}).get("request", [{}])[0].get("searchTerms") == "Playwright", \
        f"Expected 'searchTerms' to be 'Playwright', but got {response_json.get('queries', {}).get('request', [{}])[0].get('searchTerms')}"

    # Assert that 'count' matches the expected value
    assert response_json.get("queries", {}).get("request", [{}])[0].get("count") == 10, \
        f"Expected 'count' to be 10, but got {response_json.get('queries', {}).get('request', [{}])[0].get('count')}"
