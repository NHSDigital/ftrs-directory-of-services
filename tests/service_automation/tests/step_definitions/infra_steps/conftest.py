"""Pytest configuration for infra_steps tests.

This module provides pytest hooks and fixtures specific to infrastructure tests.
"""

import pytest
from utilities.testcontainers.fixtures import is_local_test_mode


def pytest_collection_modifyitems(items: list) -> None:
    """Skip tests that depend on DynamoDB GSI ordering in local mode.

    The test 'test_for_an_odscode_that_has_more_than_one_record_only_the_first_record_will_be_returned'
    relies on specific ordering behavior from DynamoDB's OdsCodeValueIndex GSI.
    This ordering is not deterministic and differs between AWS and LocalStack.
    """
    if not is_local_test_mode():
        return

    skip_marker = pytest.mark.skip(
        reason="DynamoDB GSI ordering differs in LocalStack vs AWS - test requires AWS environment"
    )

    for item in items:
        if "only_the_first_record_will_be_returned" in item.name:
            item.add_marker(skip_marker)
