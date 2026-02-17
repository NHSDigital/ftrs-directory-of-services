from pytest_bdd import given, parsers
from httpx import Client
import socket
import pytest
import pathlib
from ftrs_test_util.fixtures.context import TestContext
from ftrs_test_util.parsing import try_parse_json
from http import HTTPStatus


@given("the CRUD API is running")
def crud_api_is_running(ingest_api_client: Client) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        sock.connect((ingest_api_client.base_url.host, ingest_api_client.base_url.port))
    except Exception:
        pytest.fail("CRUD API is not running or not reachable")
    else:
        sock.close()


@given(parsers.parse('an {entity_type} is created from the file "{file_path}"'))
def load_record_into_database(
    test_context: TestContext,
    entity_type: str,
    file_path: str,
) -> None:
    """
    Load a record into the database by making a POST request to the API with the data from the specified file.
    """
    data_dir = pathlib.Path(__file__).parent.parent / "data" / entity_type
    full_file_path = data_dir / f"{file_path}.json"

    if not full_file_path.exists():
        pytest.fail(f"Data file not found: {full_file_path}")

    contents = full_file_path.read_text()
    body = try_parse_json(contents)

    response = test_context.ingest_api_client.post(
        url="/Organization",
        json=body,
    )
    assert response.status_code == HTTPStatus.CREATED, (
        f"Failed to load record into database. Expected status code {HTTPStatus.CREATED}, got {response.status_code}\nResponse body: {response.text}"
    )


@given(parsers.parse("all {entity_type}s are created from the test data files"))
def load_all_records_into_database(test_context: TestContext, entity_type: str) -> None:
    """
    Load a record into the database by making a POST request to the API with the data from the specified file.
    """
    data_dir = pathlib.Path(__file__).parent.parent / "data" / entity_type
    file_paths = data_dir.glob("*.json")

    for data_file_path in file_paths:
        contents = data_file_path.read_text()
        body = try_parse_json(contents)

        response = test_context.ingest_api_client.post(
            url="/Organization",
            json=body,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"Failed to load record into database. Expected status code {HTTPStatus.CREATED}, got {response.status_code}\nResponse body: {response.text}"
        )
