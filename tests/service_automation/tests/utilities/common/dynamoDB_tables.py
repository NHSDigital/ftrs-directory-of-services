"""DynamoDB table configurations for testing.

This module provides backwards compatibility for existing tests.
New code should import directly from ftrs_common.testing.table_config.

Example:
    # Preferred (new code):
    from ftrs_common.testing.table_config import get_table_name, get_dynamodb_table_configs

    # Legacy (still supported):
    from utilities.common.dynamoDB_tables import get_table_name, get_dynamodb_tables
"""

from ftrs_common.testing import table_config

get_dynamodb_table_configs = table_config.get_dynamodb_table_configs
get_table_name = table_config.get_table_name


def get_dynamodb_tables() -> list[dict]:
    """
    Get DynamoDB table configurations with environment-based names.

    This is a backwards-compatible wrapper around get_dynamodb_table_configs().

    Returns:
        List of table configuration dictionaries
    """
    return get_dynamodb_table_configs(
        include_core=True,
        include_triage_code=True,
        include_data_migration_state=True,
    )
