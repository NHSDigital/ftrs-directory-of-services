import chevron
from pytest_bdd import when, parsers
from ftrs_test_util.parsing import try_parse_json
from ftrs_test_util.fixtures.context import TestContext


@when(
    parsers.parse(
        'I call the CRUD API "{method} {endpoint}" endpoint with the following JSON body:'
    )
)
def make_crud_api_request_with_json_body(
    test_context: TestContext,
    method: str,
    endpoint: str,
    docstring: str,
) -> None:
    endpoint_formatted = chevron.render(endpoint, test_context.extracted_values)
    docstring_formatted = chevron.render(docstring, test_context.extracted_values)

    body = try_parse_json(docstring_formatted)

    response = test_context.ingest_api_client.request(
        method=method.upper(),
        url=endpoint_formatted,
        json=body,
    )
    test_context.last_response = response


@when(parsers.parse('I call the CRUD API "{method} {endpoint}" endpoint'))
def make_get_request(
    test_context: TestContext,
    method: str,
    endpoint: str,
) -> None:
    endpoint_formatted = chevron.render(endpoint, test_context.extracted_values)
    response = test_context.ingest_api_client.request(
        method=method.upper(),
        url=endpoint_formatted,
    )
    test_context.last_response = response
