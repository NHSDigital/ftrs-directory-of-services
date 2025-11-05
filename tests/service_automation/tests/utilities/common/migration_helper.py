"""Helper utilities for running data migration in tests."""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from urllib.parse import urlparse, unquote

from pipeline.application import DataMigrationApplication, DMSEvent
from pipeline.utils.config import DataMigrationConfig, DatabaseConfig
from pipeline.processor import DataMigrationMetrics


@dataclass
class MigrationRunResult:
    """Store results from a migration run."""

    success: bool
    error: Optional[str] = None
    application: Optional[DataMigrationApplication] = None
    metrics: Optional[DataMigrationMetrics] = None


class MigrationHelper:
    """Helper class for running data migration in tests."""

    def __init__(
        self,
        db_uri: str,
        dynamodb_endpoint: str,
        environment: str = "local",
        workspace: Optional[str] = None,
    ) -> None:
        """
        Initialize the migration helper.

        Args:
            db_uri: PostgreSQL connection URI for test database
            dynamodb_endpoint: DynamoDB endpoint URL
            environment: Environment name (default: "local")
            workspace: Optional workspace name
        """
        self.db_uri = db_uri
        self.dynamodb_endpoint = dynamodb_endpoint
        self.environment = environment
        self.workspace = workspace or "test"

    def _parse_db_uri(self) -> Dict[str, str]:
        """
        Parse database URI into component parts.

        Returns:
            Dictionary with database connection parameters
        """
        parsed = urlparse(self.db_uri)

        host = parsed.hostname or "localhost"
        port = str(parsed.port) if parsed.port else "5432"
        dbname = parsed.path.lstrip("/") if parsed.path else "postgres"
        username = unquote(parsed.username) if parsed.username else "test"
        password = unquote(parsed.password) if parsed.password else "test"

        return {
            "host": host,
            "port": port,
            "dbname": dbname,
            "username": username,
            "password": password,
        }

    def create_migration_config(self) -> DataMigrationConfig:
        """
        Create a DataMigrationConfig for testing.

        Constructs config using test database connection instead of environment variables.

        Returns:
            DataMigrationConfig instance configured for testing
        """
        db_params = self._parse_db_uri()

        db_config = DatabaseConfig(
            host=db_params["host"],
            port=db_params["port"],
            dbname=db_params["dbname"],
            username=db_params["username"],
            password=db_params["password"],
        )

        # CRITICAL: Use model_construct to bypass Pydantic validation and env var loading
        # This creates the config object directly without reading from environment
        config = DataMigrationConfig.model_construct(
            db_config=db_config,
            env=self.environment,
            workspace=self.workspace,
            dynamodb_endpoint=self.dynamodb_endpoint,
        )

        # Verify the endpoint was set correctly using actual attribute names
        print("🔍 Config verification:")
        print(f"  - dynamodb_endpoint: {config.dynamodb_endpoint}")
        print(f"  - env: {config.env}")
        print(f"  - workspace: {config.workspace}")

        return config

    def run_single_service_migration(self, service_id: int) -> MigrationRunResult:
        """
        Run migration for a single service.

        Args:
            service_id: The ID of the service to migrate

        Returns:
            MigrationRunResult with success status, error, and metrics
        """
        try:
            config = self.create_migration_config()

            # Debug logging using actual attribute names
            print("🔍 Running migration with config:")
            print(f"  - DynamoDB endpoint: {config.dynamodb_endpoint}")
            print(f"  - Environment: {config.env}")
            print(f"  - Workspace: {config.workspace}")

            app = DataMigrationApplication(config=config)

            event = DMSEvent(
                type="dms_event",
                record_id=service_id,
                table_name="services",
                method="insert",
            )

            app.handle_dms_event(event)

            metrics = app.processor.metrics if hasattr(app, "processor") else None

            return MigrationRunResult(
                success=True, application=app, metrics=metrics
            )

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback

            traceback.print_exc()
            return MigrationRunResult(success=False, error=str(e), metrics=None)

    def run_full_service_migration(self) -> MigrationRunResult:
        """
        Run full service migration.

        Returns:
            MigrationRunResult with success status, error, and metrics
        """
        try:
            config = self.create_migration_config()
            app = DataMigrationApplication(config=config)

            app.handle_full_sync_event()

            metrics = app.processor.metrics if hasattr(app, "processor") else None

            return MigrationRunResult(
                success=True, application=app, metrics=metrics
            )

        except Exception as e:
            return MigrationRunResult(success=False, error=str(e), metrics=None)

    def run_sqs_event_migration(
        self, sqs_event: Dict[str, Any]
    ) -> MigrationRunResult:
        """
        Run migration with an SQS event.

        Args:
            sqs_event: SQS event dictionary

        Returns:
            MigrationRunResult with success status, error, and metrics
        """
        try:
            config = self.create_migration_config()
            app = DataMigrationApplication(config=config)

            app.handle_sqs_event(sqs_event)

            metrics = app.processor.metrics if hasattr(app, "processor") else None

            return MigrationRunResult(
                success=True, application=app, metrics=metrics
            )

        except Exception as e:
            return MigrationRunResult(success=False, error=str(e), metrics=None)
