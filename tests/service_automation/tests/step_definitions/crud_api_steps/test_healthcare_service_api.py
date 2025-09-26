from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from utilities.infra.api_util import get_r53, get_url
from utilities.infra.dns_util import wait_for_dns


# Load feature file
scenarios("./crud_api_features/healthcare_service_api.feature")


@when(
    parsers.re(
        r'I request data from the "(?P<api_name>.*?)" endpoint "(?P<resource_name>.*?)"'
    ),
    target_fixture="fresponse",
)
def send_get(api_request_context_mtls_crud, api_name, resource_name):
    url = get_url(api_name) + "/" + resource_name
    # Handle None or empty params
    response = api_request_context_mtls_crud.get(url)
    return response
