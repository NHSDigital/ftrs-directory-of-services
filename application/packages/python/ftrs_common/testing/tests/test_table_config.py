"""Unit tests for table_config module."""

import os
from unittest.mock import patch

import pytest

from ftrs_common.testing.table_config import (
    get_core_table_configs,
    get_data_migration_state_table_config,
    get_dynamodb_table_configs,
    get_table_name,
    get_triage_code_table_config,
)


class TestGetTableName:
    """Tests for get_table_name function."""

    def test_uses_env_vars_by_default(self) -> None:
        """Should use environment variables when no explicit params provided."""
        with patch.dict(
            os.environ,
            {
                "PROJECT_NAME": "my-project",
                "ENVIRONMENT": "prod",
                "WORKSPACE": "main",
            },
        ):
            result = get_table_name("organisation")
            assert result == "my-project-prod-database-organisation-main"

    def test_explicit_params_override_env_vars(self) -> None:
        """Explicit parameters should override environment variables."""
        with patch.dict(
            os.environ,
            {
                "PROJECT_NAME": "env-project",
                "ENVIRONMENT": "env-env",
                "WORKSPACE": "env-ws",
            },
        ):
            result = get_table_name(
                "location",
                project_name="explicit-project",
                environment="explicit-env",
                workspace="explicit-ws",
            )
            assert result == "explicit-project-explicit-env-database-location-explicit-ws"

    def test_custom_stack_name(self) -> None:
        """Should use custom stack name when provided."""
        with patch.dict(
            os.environ,
            {
                "PROJECT_NAME": "ftrs-dos",
                "ENVIRONMENT": "dev",
                "WORKSPACE": "test",
            },
        ):
            result = get_table_name("state", stack_name="data-migration")
            assert result == "ftrs-dos-dev-data-migration-state-test"

    def test_defaults_when_no_env_vars(self) -> None:
        """Should use defaults when environment variables not set."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_table_name("healthcare-service")
            assert result == "ftrs-dos-dev-database-healthcare-service-test"

    def test_empty_workspace_omits_suffix(self) -> None:
        """Empty workspace should not add suffix."""
        with patch.dict(os.environ, {"WORKSPACE": ""}, clear=False):
            result = get_table_name(
                "organisation",
                project_name="proj",
                environment="env",
                workspace="",
            )
            assert result == "proj-env-database-organisation"


class TestGetCoreTableConfigs:
    """Tests for get_core_table_configs function."""

    def test_returns_three_tables(self) -> None:
        """Should return configs for organisation, location, healthcare-service."""
        configs = get_core_table_configs(
            project_name="test",
            environment="dev",
            workspace="ws",
        )
        assert len(configs) == 3

        table_names = [c["TableName"] for c in configs]
        assert "test-dev-database-organisation-ws" in table_names
        assert "test-dev-database-location-ws" in table_names
        assert "test-dev-database-healthcare-service-ws" in table_names

    def test_table_schema_structure(self) -> None:
        """Each table should have correct key schema and billing mode."""
        configs = get_core_table_configs(
            project_name="test",
            environment="dev",
            workspace="ws",
        )

        for config in configs:
            # Check key schema
            assert config["KeySchema"] == [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ]
            # Check attribute definitions
            assert config["AttributeDefinitions"] == [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
            ]
            # Check billing mode
            assert config["BillingMode"] == "PAY_PER_REQUEST"


class TestGetTriageCodeTableConfig:
    """Tests for get_triage_code_table_config function."""

    def test_includes_gsi(self) -> None:
        """Triage code table should include CodeTypeIndex GSI."""
        config = get_triage_code_table_config(
            project_name="test",
            environment="dev",
            workspace="ws",
        )

        assert "GlobalSecondaryIndexes" in config
        gsi = config["GlobalSecondaryIndexes"][0]
        assert gsi["IndexName"] == "CodeTypeIndex"
        assert gsi["KeySchema"] == [
            {"AttributeName": "codeType", "KeyType": "HASH"},
            {"AttributeName": "id", "KeyType": "RANGE"},
        ]

    def test_includes_codetype_attribute(self) -> None:
        """Should define codeType attribute for the GSI."""
        config = get_triage_code_table_config(
            project_name="test",
            environment="dev",
            workspace="ws",
        )

        attr_names = [a["AttributeName"] for a in config["AttributeDefinitions"]]
        assert "codeType" in attr_names


class TestGetDataMigrationStateTableConfig:
    """Tests for get_data_migration_state_table_config function."""

    def test_uses_data_migration_stack_name(self) -> None:
        """State table should use data-migration stack name."""
        config = get_data_migration_state_table_config(
            project_name="ftrs-dos",
            environment="dev",
            workspace="test",
        )

        assert config["TableName"] == "ftrs-dos-dev-data-migration-state-test"

    def test_simple_key_schema(self) -> None:
        """State table should only have hash key, no range key."""
        config = get_data_migration_state_table_config(
            project_name="test",
            environment="dev",
            workspace="ws",
        )

        assert config["KeySchema"] == [
            {"AttributeName": "source_record_id", "KeyType": "HASH"},
        ]


class TestGetDynamoDBTableConfigs:
    """Tests for get_dynamodb_table_configs function."""

    def test_returns_all_tables_by_default(self) -> None:
        """Should return all table configs by default."""
        configs = get_dynamodb_table_configs(
            project_name="test",
            environment="dev",
            workspace="ws",
        )

        # 3 core + 1 triage code + 1 state = 5 tables
        assert len(configs) == 5

    def test_can_exclude_core_tables(self) -> None:
        """Should be able to exclude core entity tables."""
        configs = get_dynamodb_table_configs(
            include_core=False,
            project_name="test",
            environment="dev",
            workspace="ws",
        )

        # 1 triage code + 1 state = 2 tables
        assert len(configs) == 2

    def test_can_exclude_triage_code_table(self) -> None:
        """Should be able to exclude triage code table."""
        configs = get_dynamodb_table_configs(
            include_triage_code=False,
            project_name="test",
            environment="dev",
            workspace="ws",
        )

        # 3 core + 1 state = 4 tables
        assert len(configs) == 4

    def test_can_exclude_data_migration_state(self) -> None:
        """Should be able to exclude data migration state table."""
        configs = get_dynamodb_table_configs(
            include_data_migration_state=False,
            project_name="test",
            environment="dev",
            workspace="ws",
        )

        # 3 core + 1 triage code = 4 tables
        assert len(configs) == 4

    def test_crud_apis_minimal_config(self) -> None:
        """CRUD APIs only need core tables."""
        configs = get_dynamodb_table_configs(
            include_core=True,
            include_triage_code=False,
            include_data_migration_state=False,
            project_name="ftrs-dos",
            environment="local",
            workspace="test",
        )

        assert len(configs) == 3
        table_names = [c["TableName"] for c in configs]
        assert all("database" in name for name in table_names)
