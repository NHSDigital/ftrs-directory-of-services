import pytest
import json
from pytest_bdd import given, when, then, scenarios
from playwright.sync_api import sync_playwright
from Config import config

# Load feature file
scenarios("../tests/features/api-google-search.feature")

# Load config values
BASE_URL = config.get("base_url")
API_KEY = config.get("api_key")
SEARCH_ENGINE_ID = config.get("search_engine_id")


@pytest.fixture
def api_response():
    """Fixture to store API response for logging in reports."""
    return {}


@given("I make GET request to the Google search API")
def make_google_search_request(api_request_context, api_response):
    """Make a GET request using Playwright's APIRequestContext"""
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": "Playwright"
    }
    
    response = api_request_context.get(BASE_URL, params=params)

    # Store request & response for logging
    api_response["request"] = json.dumps(params, indent=2)
    api_response["response_status"] = response.status
    api_response["response_body"] = json.dumps(response.json(), indent=2)

    # Print request & response in terminal
    print("\n--- API Request ---")
    print(json.dumps(params, indent=2))
    print("\n--- API Response ---")
    print(f"Status Code: {response.status}")
    print(json.dumps(response.json(), indent=2), flush=True)

    # Ensure response is valid
    assert response.status == 200, f"Unexpected status code: {response.status}"
    return response.json()


@when("I receive the response")
def receive_response(make_google_search_request):
    """Receive the API response"""
    return make_google_search_request


@then("I should see search results")
def verify_search_results(receive_response, api_response):
    """Verify the search results contain 'Playwright'"""
    results = receive_response.get("items", [])

    # Log assertion in pytest report
    assert any("Playwright" in result.get("title", "") for result in results), "No Playwright-related results found"

    # Store success message
    api_response["success_message"] = "Search results contain 'Playwright'."
    
    # Print success message
    print("\n Assertion Passed: Search results contain 'Playwright'.", flush=True)
