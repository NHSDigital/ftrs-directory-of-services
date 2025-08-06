from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from utilities.infra.api_util import get_r53, get_url
from utilities.infra.dns_util import wait_for_dns
from utilities.infra.secrets_util import GetSecretWrapper
from utilities.common.file_helper import create_temp_file
from loguru import logger

# Load feature file
scenarios("./is_api_features/gp_search_api.feature")


@given(parsers.re(r'the dns for "(?P<api_name>.*?)" is resolvable'))
def dns_resolvable(api_name, env, workspace):
    r53 = get_r53(workspace, api_name, env)
    assert wait_for_dns(r53) == True


@when(
    parsers.re(r'I request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)" with query params "(?P<params>.*?)"'),
    target_fixture="fresponse",
)
def send_get_with_params(
    api_request_context_mtls, workspace, api_name, env, params, resource_name
):
    url = get_url(workspace, api_name, env) + "/" + resource_name
    # Handle None or empty params
    if params is None or not params.strip():
        param_dict = {}
    else:
        # Parse the params string into a dictionary
        param_dict = dict(param.split('=', 1) for param in params.split('&') if '=' in param)

    response = api_request_context_mtls.get(
            url,  params=param_dict
        )
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


@then(parsers.parse('I receive the diagnostics "{diagnostics}"'))
def api_diagnostics(fresponse, diagnostics):
    response = fresponse.json()
    assert (response["issue"][0]["diagnostics"]).startswith(diagnostics)


@then('the response body contains a bundle')
def api_check_bundle(fresponse):
    response = fresponse.json()
    assert response["resourceType"] == "Bundle"


@then(parsers.parse('the bundle contains "{number:d}" "{resource_type}" resources'))
def api_number_resources(fresponse, number, resource_type):
    response = fresponse.json()
    assert count_resources(response, resource_type) == number


@then(parsers.parse('the response body contains JSON with a key "{key}" and value "{value}"'))
def api_json_key_value(fresponse, key, value):
    response = fresponse.json()
    assert response[key] == value


@then(parsers.parse('the response body contains an "{resource_type}" resource'))
def api_check_resource_type(fresponse, resource_type):
    response = fresponse.json()
    assert response["resourceType"] == resource_type


@then(parsers.parse('the resource has an id of "{resource_id}"'))
def api_check_resource_id(fresponse, resource_id):
    response = fresponse.json()
    assert response["id"] == resource_id


def count_resources(lambda_response, resource_type):
    return sum(
        entry.get("resource", {}).get("resourceType") == resource_type
        for entry in lambda_response.get("entry", [])
    )


