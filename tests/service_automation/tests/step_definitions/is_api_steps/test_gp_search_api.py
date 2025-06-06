import pytest
import json
from pytest_bdd import scenarios, given, when, then, parsers
from loguru import logger
from utilities.infra.api_util import get_url
from step_definitions.common_steps.setup_steps import *

# Load feature file
scenarios("./is_api_features/gp_search_api.feature")


@given(parsers.parse('I request data for "{params}" from "{resource_name}"'), target_fixture='fresponse')
def send_get_with_params(api_request_context, workspace, fstack_name, project, env, params, resource_name):
    url = get_url( workspace, fstack_name, project, env) + "/" + resource_name
    response = api_request_context.get(url, params=params)
    return response


@then(parsers.parse('I receive a status code "{status_code}" in response'))
def status_code(fresponse, status_code):
    assert fresponse.status == int(status_code)


@then(parsers.parse('I receive the error code "{error_code}"'))
def api_error_code(fresponse, error_code):
    response = fresponse.json()
    assert response["issue"][0]["details"]["coding"][0]["code"] == error_code

@then(parsers.parse('I receive the message "{error_message}"'))
def api__error_message(fresponse, error_message):
    response = fresponse.json()
    assert response["issue"][0]["details"]["text"] == (error_message)


@then(parsers.parse('I receive the diagnostics "{diagnostics}"'))
def api__diagnostics(fresponse, diagnostics):
    response = fresponse.json()
    assert (response["issue"][0]["diagnostics"]).startswith(diagnostics)
