"""Feature flag step definitions for BDD tests."""

import os
from typing import Generator

from ftrs_common.feature_flags.feature_flags_client import _get_client
from pytest_bdd import given, parsers


@given(
    parsers.parse("the feature flag '{flag_name}' is set to '{flag_value}'"),
    target_fixture="feature_flag_set",
)
def set_feature_flag(flag_name: str, flag_value: str) -> Generator[None, None, None]:
    """
    Set a feature flag environment variable for the duration of the test.

    Args:
        flag_name: Name of the feature flag environment variable
        flag_value: Value to set ("true" or "false")

    Yields:
        None

    Cleanup:
        Restores the original environment variable value after the test
        and clears the feature flags client cache
    """
    original_value = os.environ.get(flag_name)

    # Clear the cache before setting the new value to ensure fresh client
    _get_client.cache_clear()

    try:
        os.environ[flag_name] = flag_value
        yield
    finally:
        # Restore original value or remove the key if it didn't exist
        if original_value is not None:
            os.environ[flag_name] = original_value
        elif flag_name in os.environ:
            del os.environ[flag_name]

        # Clear cache to ensure next test gets fresh client
        _get_client.cache_clear()
