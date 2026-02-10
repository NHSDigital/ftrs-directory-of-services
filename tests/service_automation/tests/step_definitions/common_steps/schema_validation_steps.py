from pathlib import Path

from loguru import logger
from pytest_bdd import parsers, then
from utilities.infra.schema_validator import validate_api_response


@then(
    parsers.re(
        r'the response is valid against the (?P<api_name>.*?) schema for endpoint "(?P<endpoint_path>.*?)"'
    )
)
def validate_response_against_dos_search_schema(
    fresponse, api_name: str, endpoint_path: str
) -> None:
    """
    Validate the API response against the OpenAPI schema.
    Args:
        fresponse: The API response fixture
        endpoint_path: The API endpoint path (e.g., "/Organization")
    """
    # Path to the yaml schema file - navigate from current file to repo root
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[
        5
    ]  # Go up: is_api_steps -> step_definitions -> tests -> service_automation -> tests -> repo_root

    schema_path = repo_root / "docs" / "specification" / (api_name + ".yaml")

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    # Get response data
    response_data = fresponse.json()
    status_code = str(fresponse.status)

    # Validate response
    is_valid, error_msg = validate_api_response(
        response_data=response_data,
        schema_path=str(schema_path),
        endpoint_path=endpoint_path,
        method="get",
        status_code=status_code,
    )

    assert is_valid, f"Response validation failed: {error_msg}"
    logger.info(f"Response successfully validated against schema for {endpoint_path}")
