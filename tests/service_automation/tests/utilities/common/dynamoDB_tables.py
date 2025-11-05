"""DynamoDB table configurations for testing."""
import os
from typing import Any


def get_table_name(resource: str) -> str:
    """
    Generate DynamoDB table name using environment variables.

    Pattern: {PROJECT_NAME}-{ENVIRONMENT}-database-{resource}-{WORKSPACE}

    Args:
        resource: Resource type (e.g., 'organisation', 'location', 'healthcare-service')

    Returns:
        Full table name following project naming convention
    """
    project_name = os.getenv("PROJECT_NAME", "ftrs-dos")
    environment = os.getenv("ENVIRONMENT", "dev")
    workspace = os.getenv("WORKSPACE", "test")

    return f"{project_name}-{environment}-database-{resource}-{workspace}"


def get_dynamodb_tables() -> list[dict[str, Any]]:
    """
    Get DynamoDB table configurations with environment-based names.

    Returns:
        List of table configuration dictionaries
    """
    resources = ["organisation", "location", "healthcare-service"]

    return [
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
