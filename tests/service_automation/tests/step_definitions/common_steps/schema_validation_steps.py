from pathlib import Path

from loguru import logger
from playwright.sync_api import APIResponse
from pytest_bdd import parsers, then
from utilities.infra.schema_validator import validate_api_response


def _find_repo_root(start: Path, marker: str = ".git") -> Path:
    """Walk parent directories from *start* until *marker* is found.

    Args:
        start: The starting directory.
        marker: Name of the file or directory that identifies the repo root.

    Returns:
        The repository root path.

    Raises:
        FileNotFoundError: If no parent contains the marker.
    """
    current = start if start.is_dir() else start.parent
    for parent in (current, *current.parents):
        if (parent / marker).exists():
            return parent
    raise FileNotFoundError(
        f"Could not find repo root: no '{marker}' marker in any parent of {start}"
    )


@then(
    parsers.re(
        r'the response is valid against the (?P<api_name>.*?) schema for endpoint "(?P<endpoint_path>.*?)"'
    )
)
def validate_response_against_dos_search_schema(
    fresponse: APIResponse, api_name: str, endpoint_path: str
) -> None:
    """
    Validate the API response against the OpenAPI schema.
    Args:
        fresponse: The API response fixture
        endpoint_path: The API endpoint path (e.g., "/Organization")
    """
    # Derive repo root by walking up to the .git marker
    repo_root = _find_repo_root(Path(__file__).resolve())

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
