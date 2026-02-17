from dataclasses import dataclass, field
import httpx
import pytest


@dataclass
class TestContext:
    ingest_api_client: httpx.Client
    last_response: httpx.Response | None
    extracted_values: dict


@pytest.fixture
def test_context(ingest_api_client: httpx.Client) -> TestContext:
    return TestContext(
        ingest_api_client=ingest_api_client,
        last_response=None,
        extracted_values={},
    )
