"""Helper utilities for running data migration in tests."""
import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
from unittest.mock import patch
from urllib.parse import unquote, urlparse

from aws_lambda_powertools.utilities.data_classes import SQSEvent
from ftrs_common.mocks.mock_logger import MockLogger
from loguru import logger

from pipeline.application import DataMigrationApplication, DMSEvent
from pipeline.processor import DataMigrationMetrics
from pipeline.utils.config import DatabaseConfig, DataMigrationConfig

# Type aliases
DbParams = Dict[str, str]
MigrationExecutor = Callable[[DataMigrationApplication], None]


@dataclass
class MigrationRunResult:
    """Store results from a migration run."""

    success: bool
    error: Optional[str] = None
    application: Optional[DataMigrationApplication] = None
    metrics: Optional[DataMigrationMetrics] = None
    mock_logger: Optional[MockLogger] = None


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
            workspace: Optional workspace name (defaults to "test")
        """
        self.db_uri = db_uri
        self.dynamodb_endpoint = dynamodb_endpoint
        self.environment = environment
        self.workspace = workspace or "test"

    def _parse_db_uri(self) -> DbParams:
        """
        Parse database URI into component parts.

        Returns:
            Dictionary with database connection parameters
        """
        parsed = urlparse(self.db_uri)

        return {
            "host": parsed.hostname or "localhost",
            "port": str(parsed.port) if parsed.port else "5432",
            "dbname": parsed.path.lstrip("/") if parsed.path else "postgres",
            "username": unquote(parsed.username) if parsed.username else "test",
            "password": unquote(parsed.password) if parsed.password else "test",
        }

    @contextmanager
    def _localstack_credentials(self):
        """
        Context manager for setting and restoring AWS credentials.

        Yields:
            None

        Example:
            with self._localstack_credentials():
                # Use LocalStack with dummy credentials
                pass
            # Original credentials restored automatically
        """
        # Store original values
        original_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        original_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        original_session_token = os.environ.get("AWS_SESSION_TOKEN")

        try:
            # Set dummy credentials for LocalStack
            os.environ["AWS_ACCESS_KEY_ID"] = "test"
            os.environ["AWS_SECRET_ACCESS_KEY"] = "test"

            # Remove session token if present
            if "AWS_SESSION_TOKEN" in os.environ:
                del os.environ["AWS_SESSION_TOKEN"]

            logger.debug("Set dummy AWS credentials for LocalStack")
            yield

        finally:
            # Restore original credentials
            if original_access_key:
                os.environ["AWS_ACCESS_KEY_ID"] = original_access_key
            elif "AWS_ACCESS_KEY_ID" in os.environ:
                del os.environ["AWS_ACCESS_KEY_ID"]

            if original_secret_key:
                os.environ["AWS_SECRET_ACCESS_KEY"] = original_secret_key
            elif "AWS_SECRET_ACCESS_KEY" in os.environ:
                del os.environ["AWS_SECRET_ACCESS_KEY"]

            if original_session_token:
                os.environ["AWS_SESSION_TOKEN"] = original_session_token

            logger.debug("Restored original AWS credentials")

    def create_migration_config(self) -> DataMigrationConfig:
        """
        Create a DataMigrationConfig for testing.

        Uses model_construct to bypass Pydantic's environment variable loading,
        allowing explicit configuration values for testing.

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

        config = DataMigrationConfig.model_construct(
            db_config=db_config,
            env=self.environment,
            workspace=self.workspace,
            dynamodb_endpoint=self.dynamodb_endpoint,
        )

        return config

    def _get_metrics_from_app(
        self, app: Optional[DataMigrationApplication]
    ) -> Optional[DataMigrationMetrics]:
        """
        Safely retrieve metrics from application.

        Args:
            app: DataMigrationApplication instance or None

        Returns:
            DataMigrationMetrics if available, otherwise None
        """
        if app and hasattr(app, "processor") and app.processor:
            return app.processor.metrics
        return None

    def _log_mock_logger_stats(self, mock_logger: MockLogger) -> None:
        """
        Log MockLogger capture statistics.

        Args:
            mock_logger: MockLogger instance to inspect
        """
        log_count = mock_logger.get_log_count()
        logger.info(f"MockLogger captured {log_count} logs")

        if log_count > 0:
            references = list(
                set([log.get("reference") for log in mock_logger.get_logs()])
            )
            logger.debug(f"Log references: {references}")

    def _execute_migration(
        self,
        migration_fn: MigrationExecutor,
        migration_type: str,
    ) -> MigrationRunResult:
        """
        Execute a migration with common error handling and logging.

        Args:
            migration_fn: Function that executes the migration on the app
            migration_type: Description of migration type for logging

        Returns:
            MigrationRunResult with success status, metrics, and mock_logger

        Example:
            result = self._execute_migration(
                lambda app: app.handle_dms_event(event),
                "single service"
            )
        """
        mock_logger = MockLogger(service="data-migration")
        app = None

        try:
            with self._localstack_credentials():
                config = self.create_migration_config()

                with patch("ftrs_common.logger.Logger.get", return_value=mock_logger):
                    app = DataMigrationApplication(config=config)
                    migration_fn(app)

            # Get metrics
            metrics = self._get_metrics_from_app(app)

            # Log statistics
            self._log_mock_logger_stats(mock_logger)

            return MigrationRunResult(
                success=True,
                application=app,
                metrics=metrics,
                mock_logger=mock_logger,
            )

        except Exception as e:
            logger.error(
                f"{migration_type.capitalize()} migration failed: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )

            metrics = self._get_metrics_from_app(app)
            if metrics:
                logger.info(f"Retrieved metrics despite error: {metrics}")

            return MigrationRunResult(
                success=False,
                error=str(e),
                metrics=metrics,
                mock_logger=mock_logger,
            )

    def run_single_service_migration(self, service_id: int) -> MigrationRunResult:
        """
        Run migration for a single service.

        Args:
            service_id: The ID of the service to migrate

        Returns:
            MigrationRunResult with success status, error, and metrics
        """

        def execute(app: DataMigrationApplication) -> None:
            event = DMSEvent(
                type="dms_event",
                record_id=service_id,
                table_name="services",
                method="insert",
            )
            logger.info(f"Running single service migration for service ID: {service_id}")
            app.handle_dms_event(event)

        return self._execute_migration(execute, f"single service (ID: {service_id})")

    def run_full_service_migration(self) -> MigrationRunResult:
        """
        Run full service migration.

        Returns:
            MigrationRunResult with success status, error, and metrics
        """

        def execute(app: DataMigrationApplication) -> None:
            logger.info("Running full service migration")
            app.handle_full_sync_event()

        return self._execute_migration(execute, "full service")

    def run_sqs_event_migration(self, sqs_event: Dict[str, Any]) -> MigrationRunResult:
        """
        Run migration with an SQS event.

        Args:
            sqs_event: SQS event dictionary

        Returns:
            MigrationRunResult with success status, error, and metrics
        """

        def execute(app: DataMigrationApplication) -> None:
            record_count = len(sqs_event.get("Records", []))
            logger.info(f"Running SQS event migration with {record_count} record(s)")
            sqs_event_obj = SQSEvent(sqs_event)
            app.handle_sqs_event(sqs_event_obj)

        return self._execute_migration(execute, "SQS event")
