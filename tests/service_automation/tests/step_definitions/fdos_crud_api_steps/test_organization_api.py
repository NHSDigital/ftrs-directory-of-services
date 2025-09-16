from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from utilities.infra.api_util import get_r53, get_url
from utilities.infra.dns_util import wait_for_dns


# Load feature file
scenarios("./fdos_crud_api_features/fdos_crud_organization_api.feature")


@given(parsers.re(r'the dns for "(?P<api_name>.*?)" is resolvable'))
def dns_resolvable(api_name, env, workspace):
    r53 = get_r53(workspace, api_name, env)
    assert wait_for_dns(r53)


@when(
    parsers.re(r'I request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)"'),
    target_fixture="fresponse",
)
def send_get(api_request_context, api_name, resource_name):
    url = get_url(api_name) + "/" + resource_name
    # Handle None or empty params
    response = api_request_context.get(url)
    return response


@then(parsers.parse('I receive a status code "{status_code:d}" in response'))
def status_code(fresponse, status_code):
    assert fresponse.status == status_code


@then(parsers.parse('I receive the error code "{error_code}"'))
def api_error_code(fresponse, error_code):
    response = fresponse.json()
    assert response["issue"][0]["details"]["coding"][0]["code"] == error_code


@then(parsers.parse('I receive the message "{error_message}"'))
def api_error_message(fresponse, error_message):
    response = fresponse.json()
    assert response["issue"][0]["details"]["text"] == (error_message)


@then('the response body contains a bundle')
def api_check_bundle(fresponse):
    response = fresponse.json()
    assert response["resourceType"] == "Bundle"


@then(parsers.parse('the bundle contains "{number:d}" "{resource_type}" resources'))
def api_number_resources(fresponse, number, resource_type):
    response = fresponse.json()
    assert count_resources(response, resource_type) == number


def count_resources(lambda_response, resource_type):
    return sum(
        entry.get("resource", {}).get("resourceType") == resource_type
        for entry in lambda_response.get("entry", [])
    )
