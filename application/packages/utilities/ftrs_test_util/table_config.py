"""DynamoDB table configurations for testing.

This module provides table schema definitions that can be used to create
DynamoDB tables in LocalStack or other test environments.
"""

import os
from typing import Any
from ftrs_common.utils.db_service import format_table_name


def get_core_table_configs(
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
            "TableName": format_table_name("organisation", environment, workspace),
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
            "TableName": format_table_name(
                "healthcare-service", environment, workspace
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
            "TableName": format_table_name("location", environment, workspace),
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
        "TableName": format_table_name("triage-code", environment, workspace),
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
        "TableName": format_table_name(
            "state",
            environment,
            workspace,
            stack="data-migration",
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
            get_core_table_configs(environment=environment, workspace=workspace)
        )

    if include_triage_code:
        tables.append(
            get_triage_code_table_config(environment=environment, workspace=workspace)
        )

    if include_data_migration_state:
        tables.append(
            get_data_migration_state_table_config(
                environment=environment, workspace=workspace
            )
        )

    return tables
