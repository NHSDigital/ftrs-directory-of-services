from typing import Generator
from testcontainers.localstack import LocalStackContainer
import pytest


@pytest.fixture(scope="session")
def localstack_container() -> Generator[LocalStackContainer, None, None]:
    """
    Provides a LocalStack container for testing AWS services locally.
    """
    with LocalStackContainer(image="localstack/localstack:latest") as container:
        yield container
