import requests
from pytest_bdd import given, when, then, scenarios

scenarios('../rest_api.feature')

@given("the REST API is running")
def rest_api_running():
    # Assuming WireMock is already running
    pass

@when('I send a GET request to "/api/user/1"')
def send_rest_request(context):
    context.response = requests.get("http://localhost:8080/api/user/1")

@then("the response status code should be 200")
def check_status_code(context):
    assert context.response.status_code == 200

@then('the response should contain "John Doe"')
def check_response_body(context):
    assert "John Doe" in context.response.text
