"""DynamoDB table configurations for testing.

This module provides table schema definitions that can be used to create
DynamoDB tables in LocalStack or other test environments.
"""

import os
from typing import Any


def get_table_name(
    resource: str,
    stack_name: str = "database",
    project_name: str | None = None,
    environment: str | None = None,
    workspace: str | None = None,
) -> str:
    """
    Generate DynamoDB table name using environment variables or explicit parameters.

    Pattern: {PROJECT_NAME}-{ENVIRONMENT}-{stack_name}-{resource}-{WORKSPACE}

    Args:
        resource: Resource type (e.g., 'organisation', 'location', 'healthcare-service')
        stack_name: Stack name component (default: 'database')
        project_name: Project name override (defaults to PROJECT_NAME env var)
        environment: Environment override (defaults to ENVIRONMENT env var)
        workspace: Workspace override (defaults to WORKSPACE env var)

    Returns:
        Full table name following project naming convention
    """
    project = project_name or os.getenv("PROJECT_NAME", "ftrs-dos")
    env = environment or os.getenv("ENVIRONMENT", "dev")
    ws = workspace or os.getenv("WORKSPACE", "test")

    table_name = f"{project}-{env}-{stack_name}-{resource}"

    if ws:
        table_name = f"{table_name}-{ws}"

    return table_name


def get_core_table_configs(
    project_name: str | None = None,
    environment: str | None = None,
    workspace: str | None = None,
) -> list[dict[str, Any]]:
    """
    Get core entity table configurations (organisation, location, healthcare-service).

    These are the primary tables used by CRUD APIs and DOS Search.
    Includes GSIs required for querying by ODS code, location, etc.

    Args:
        project_name: Project name override
        environment: Environment override
        workspace: Workspace override

    Returns:
        List of table configuration dictionaries
    """
    tables = []

    # Organisation table with OdsCodeValueIndex GSI
    tables.append(
        {
            "TableName": get_table_name(
                "organisation",
                project_name=project_name,
                environment=environment,
                workspace=workspace,
            ),
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
                {"AttributeName": "identifier_ODS_ODSCode", "AttributeType": "S"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "OdsCodeValueIndex",
                    "KeySchema": [
                        {"AttributeName": "identifier_ODS_ODSCode", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            "BillingMode": "PAY_PER_REQUEST",
        }
    )

    # Healthcare-service table with ProvidedByValueIndex and LocationIndex GSIs
    tables.append(
        {
            "TableName": get_table_name(
                "healthcare-service",
                project_name=project_name,
                environment=environment,
                workspace=workspace,
            ),
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
                        {"AttributeName": "providedBy", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "LocationIndex",
                    "KeySchema": [
                        {"AttributeName": "location", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            "BillingMode": "PAY_PER_REQUEST",
        }
    )

    # Location table with managingOrganization GSI
    tables.append(
        {
            "TableName": get_table_name(
                "location",
                project_name=project_name,
                environment=environment,
                workspace=workspace,
            ),
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
                {"AttributeName": "managingOrganization", "AttributeType": "S"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "ManagingOrganizationIndex",
                    "KeySchema": [
                        {"AttributeName": "managingOrganization", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            "BillingMode": "PAY_PER_REQUEST",
        }
    )

    return tables


def get_triage_code_table_config(
    project_name: str | None = None,
    environment: str | None = None,
    workspace: str | None = None,
) -> dict[str, Any]:
    """
    Get triage code table configuration with GSI.

    Args:
        project_name: Project name override
        environment: Environment override
        workspace: Workspace override

    Returns:
        Table configuration dictionary
    """
    return {
        "TableName": get_table_name(
            "triage-code",
            project_name=project_name,
            environment=environment,
            workspace=workspace,
        ),
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


def get_data_migration_state_table_config(
    project_name: str | None = None,
    environment: str | None = None,
    workspace: str | None = None,
) -> dict[str, Any]:
    """
    Get data migration state table configuration.

    Args:
        project_name: Project name override
        environment: Environment override
        workspace: Workspace override

    Returns:
        Table configuration dictionary
    """
    return {
        "TableName": get_table_name(
            "state",
            stack_name="data-migration",
            project_name=project_name,
            environment=environment,
            workspace=workspace,
        ),
        "KeySchema": [
            {"AttributeName": "source_record_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "source_record_id", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }


def get_dynamodb_table_configs(
    include_core: bool = True,
    include_triage_code: bool = True,
    include_data_migration_state: bool = True,
    project_name: str | None = None,
    environment: str | None = None,
    workspace: str | None = None,
) -> list[dict[str, Any]]:
    """
    Get all DynamoDB table configurations with environment-based names.

    Args:
        include_core: Include core entity tables (org, location, healthcare-service)
        include_triage_code: Include triage code table
        include_data_migration_state: Include data migration state table
        project_name: Project name override
        environment: Environment override
        workspace: Workspace override

    Returns:
        List of table configuration dictionaries
    """
    tables: list[dict[str, Any]] = []

    if include_core:
        tables.extend(
            get_core_table_configs(
                project_name=project_name,
                environment=environment,
                workspace=workspace,
            )
        )

    if include_triage_code:
        tables.append(
            get_triage_code_table_config(
                project_name=project_name,
                environment=environment,
                workspace=workspace,
            )
        )

    if include_data_migration_state:
        tables.append(
            get_data_migration_state_table_config(
                project_name=project_name,
                environment=environment,
                workspace=workspace,
            )
        )

    return tables
