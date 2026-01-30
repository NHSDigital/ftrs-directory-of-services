"""DynamoDB table configurations for testing."""

import os
from typing import Any


def get_table_name(resource: str, stack_name: str = "database") -> str:
    """
    Generate DynamoDB table name using environment variables.

    Pattern for data-migration tables: {PROJECT_NAME}-{ENVIRONMENT}-{resource}-{WORKSPACE}
    Pattern for other tables: {PROJECT_NAME}-{ENVIRONMENT}-database-{resource}-{WORKSPACE}

    Args:
        resource: Resource type (e.g., 'organisation', 'location', 'healthcare-service', 'data-migration-state')

    Returns:
        Full table name following project naming convention
    """
    project_name = os.getenv("PROJECT_NAME", "ftrs-dos")
    environment = os.getenv("ENVIRONMENT", "dev")
    workspace = os.getenv("WORKSPACE", "test")
    table_name = f"{project_name}-{environment}-{stack_name}-{resource}"

    if workspace:
        table_name = f"{table_name}-{workspace}"

    return table_name


def get_dynamodb_tables() -> list[dict[str, Any]]:
    """
    Get DynamoDB table configurations with environment-based names.

    Returns:
        List of table configuration dictionaries
    """
    resources = ["organisation", "location", "healthcare-service"]
    tables = [
        {
            "TableName": get_table_name(resource),
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
            ],
            "BillingMode": "PAY_PER_REQUEST",
        }
        for resource in resources
    ]

    triage_code_table = {
        "TableName": get_table_name("triage-code"),
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "field", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "field", "AttributeType": "S"},
            {"AttributeName": "codeType", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "CodeTypeIndex",
                "KeySchema": [
                    {"AttributeName": "codeType", "KeyType": "HASH"},
                    {"AttributeName": "id", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }

    state_table = {
        "TableName": get_table_name("state", stack_name="data-migration"),
        "KeySchema": [
            {"AttributeName": "source_record_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "source_record_id", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }

    return [*tables, triage_code_table, state_table]
