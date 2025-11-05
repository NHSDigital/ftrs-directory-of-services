"""DynamoDB table configurations for testing."""
import os
from typing import List, Dict, Any

dynamodb_tables = [
    {
        "TableName": "organisation",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "field", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "field", "AttributeType": "S"},
            {
                "AttributeName": "identifier_ODS_ODSCode",
                "AttributeType": "S",
            },
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "OdsCodeValueIndex",
                "KeySchema": [
                    {
                        "AttributeName": "identifier_ODS_ODSCode",
                        "KeyType": "HASH",
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        "BillingMode": "PAY_PER_REQUEST"
    },
    {
        "TableName": "healthcare-service",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "field", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "field", "AttributeType": "S"},
            {"AttributeName": "providedBy", "AttributeType": "S"},
            {"AttributeName": "location", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "ProvidedByValueIndex",
                "KeySchema": [
                    {
                        "AttributeName": "providedBy",
                        "KeyType": "HASH",
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "LocationIndex",
                "KeySchema": [
                    {
                        "AttributeName": "location",
                        "KeyType": "HASH",
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST"
    },
    {
        "TableName": "location",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "field", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "field", "AttributeType": "S"},
            {"AttributeName": "managingOrganisation", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "ManagingOrganisationIndex",
                "KeySchema": [
                    {
                        "AttributeName": "managingOrganisation",
                        "KeyType": "HASH",
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        "BillingMode": "PAY_PER_REQUEST"
    },
    {
        "TableName": "triage-code",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "field", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "field", "AttributeType": "S"},
            {"AttributeName": "codeType", "AttributeType": "S"},
            {"AttributeName": "codeID", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "CodeTypeIndex",
                "KeySchema": [
                    {
                        "AttributeName": "codeType",
                        "KeyType": "HASH",
                    },
                    {
                        "AttributeName": "id",
                        "KeyType": "RANGE",
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],

        "BillingMode": "PAY_PER_REQUEST"
    }
]


def get_table_name(resource: str) -> str:
    """
    Generate DynamoDB table name using environment variables.

    Pattern: {PROJECT_NAME}-{ENVIRONMENT}-database-{resource}-{WORKSPACE}

    Args:
        resource: Resource type (e.g., 'organisation', 'location', 'healthcare-service')

    Returns:
        Full table name following the project naming convention
    """
    project_name = os.getenv("PROJECT_NAME", "ftrs-dos")
    environment = os.getenv("ENVIRONMENT", "dev")
    workspace = os.getenv("WORKSPACE", "test")

    return f"{project_name}-{environment}-database-{resource}-{workspace}"


def get_dynamodb_tables() -> List[Dict[str, Any]]:
    """
    Get DynamoDB table configurations with names from environment variables.

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


# Export for backward compatibility - call the function to get tables
dynamodb_tables = get_dynamodb_tables()
