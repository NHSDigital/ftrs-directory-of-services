"""Helper utilities for running data migration in tests."""

from datetime import datetime
import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generator, Optional
from unittest.mock import MagicMock, patch
from urllib.parse import unquote, urlparse

from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from ftrs_common.mocks.mock_logger import MockLogger
from loguru import logger

from reference_data_load.application import (
    ReferenceDataLoadApplication,
    ReferenceDataLoadConfig,
    ReferenceDataLoadEvent,
)
from service_migration.application import ServiceMigrationApplication, DMSEvent

from service_migration.config import ServiceMigrationConfig
from service_migration.processor import ServiceMigrationMetrics
from common.config import DatabaseConfig

# Constants
TEST_AWS_REGION = "eu-west-2"
TEST_SQS_QUEUE_NAME = "test-queue"

# Type aliases
DbParams = Dict[str, str]
MigrationExecutor = Callable[[ServiceMigrationApplication], None]


@dataclass
class MigrationRunResult:
    """Store results from a migration run."""

    success: bool
    error: Optional[str] = None
    application: Optional[
        ServiceMigrationApplication | ReferenceDataLoadApplication
    ] = None
    metrics: Optional[ServiceMigrationMetrics] = None
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
    def _localstack_credentials(self) -> Generator[None, None, None]:
        """
        Context manager for setting and restoring AWS credentials and region.

        Yields:
            None
        """
        original_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        original_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        original_session_token = os.environ.get("AWS_SESSION_TOKEN")
        original_region = os.environ.get("AWS_DEFAULT_REGION")

        try:
            os.environ["AWS_ACCESS_KEY_ID"] = "test"
            os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
            os.environ["AWS_DEFAULT_REGION"] = TEST_AWS_REGION

            if "AWS_SESSION_TOKEN" in os.environ:
                del os.environ["AWS_SESSION_TOKEN"]

            logger.debug("Set dummy AWS credentials and region for LocalStack")
            yield

        finally:
            for key, original_value in [
                ("AWS_ACCESS_KEY_ID", original_access_key),
                ("AWS_SECRET_ACCESS_KEY", original_secret_key),
                ("AWS_SESSION_TOKEN", original_session_token),
                ("AWS_DEFAULT_REGION", original_region),
            ]:
                if original_value:
                    os.environ[key] = original_value
                elif key in os.environ:
                    del os.environ[key]

            logger.debug("Restored original AWS credentials and region")

    def create_migration_config(self) -> ServiceMigrationConfig:
        """
        Create a DataMigrationConfig for testing.

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

        config = ServiceMigrationConfig.model_construct(
            db_config=db_config,
            env=self.environment,
            workspace=self.workspace,
            dynamodb_endpoint=self.dynamodb_endpoint,
        )

        return config

    def _get_metrics_from_app(
        self, app: Optional[ServiceMigrationApplication]
    ) -> Optional[ServiceMigrationMetrics]:
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
                set(
                    [
                        log.get("reference")
                        for log in mock_logger.get_logs()
                        if log.get("reference")
                    ]
                )
            )
            if references:
                logger.debug(f"Log references: {references}")

    def _create_sqs_record_from_dms_event(self, dms_event: DMSEvent) -> SQSRecord:
        """
        Create a mock SQSRecord containing a DMSEvent.

        Matches the format expected by handle_sqs_record.

        Args:
            dms_event: The DMSEvent to wrap in an SQS record

        Returns:
            SQSRecord containing the DMSEvent in its body
        """
        timestamp_ms = str(int(datetime.now().timestamp() * 1000))

        return SQSRecord(
            data={
                "messageId": f"test-service-{dms_event.service_id}",
                "body": dms_event.model_dump_json(),
                "receiptHandle": f"test-receipt-handle-{dms_event.record_id}",
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": timestamp_ms,
                    "SenderId": "test-sender",
                    "ApproximateFirstReceiveTimestamp": timestamp_ms,
                },
                "messageAttributes": {},
                "md5OfBody": f"test-md5-{dms_event.record_id}",
                "eventSource": "aws:sqs",
                "awsRegion": TEST_AWS_REGION,
            }
        )

    def _create_mock_lambda_context(self) -> MagicMock:
        """
        Create a mock Lambda context for testing.

        Returns:
            MagicMock object configured with Lambda context attributes
        """
        current_date = datetime.now().strftime("%Y/%m/%d")

        mock_context = MagicMock()
        mock_context.function_name = "test-migration-function"
        mock_context.memory_limit_in_mb = 512
        mock_context.aws_request_id = "test-request-id"
        mock_context.log_group_name = "/aws/lambda/test-migration-function"
        mock_context.log_stream_name = f"{current_date}/[$LATEST]test-request-id"
        mock_context.get_remaining_time_in_millis = lambda: 300000

        return mock_context

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
        """
        mock_logger = MockLogger(service="data-migration")
        app = None

        try:
            with self._localstack_credentials():
                config = self.create_migration_config()

                with patch("ftrs_common.logger.Logger.get", return_value=mock_logger):
                    app = ServiceMigrationApplication(config=config)
                    migration_fn(app)

            metrics = self._get_metrics_from_app(app)
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

    # def run_single_service_migration(self, service_id: int) -> MigrationRunResult:
    #     """
    #     Run migration for a single service.

    #     Args:
    #         service_id: The ID of the service to migrate

    #     Returns:
    #         MigrationRunResult with success status, error, and metrics
    #     """

    #     def execute(app: ServiceMigrationApplication) -> None:
    #         dms_event = DMSEvent(
    #             record_id=service_id,
    #             service_id=service_id,
    #             table_name="services",
    #             method="insert",
    #         )

    #         sqs_record = self._create_sqs_record_from_dms_event(dms_event)

    #         logger.info(
    #             f"Running single service migration for service ID: {service_id}"
    #         )
    #         app.handle_sqs_record(sqs_record)

    #     return self._execute_migration(execute, f"single service (ID: {service_id})")

    # def run_full_service_migration(self) -> MigrationRunResult:
    #     """
    #     Run full service migration.

    #     Returns:
    #         MigrationRunResult with success status, error, and metrics
    #     """

    #     def execute(app: ServiceMigrationApplication) -> None:
    #         logger.info("Running full service migration")
    #         app.handle_full_sync_event()

    #     return self._execute_migration(execute, "full service")

    def run_triage_code_migration_only(self):
        """
        Run migration for only triage-code table.

        Returns:
            MigrationRunResult with success status, error, and metrics
        """

        mock_logger = MockLogger(service="data-migration")
        app = None

        try:
            with self._localstack_credentials():
                db_params = self._parse_db_uri()
                db_config = DatabaseConfig(
                    host=db_params["host"],
                    port=db_params["port"],
                    dbname=db_params["dbname"],
                    username=db_params["username"],
                    password=db_params["password"],
                )

                config = ReferenceDataLoadConfig.model_construct(
                    db_config=db_config,
                    env=self.environment,
                    workspace=self.workspace,
                    dynamodb_endpoint=self.dynamodb_endpoint,
                )

                with patch("ftrs_common.logger.Logger.get", return_value=mock_logger):
                    app = ReferenceDataLoadApplication(config)
                    app.handle(ReferenceDataLoadEvent(type="triagecode"))

            metrics = self._get_metrics_from_app(app)
            self._log_mock_logger_stats(mock_logger)

            return MigrationRunResult(
                success=True,
                application=app,
                metrics=metrics,
                mock_logger=mock_logger,
            )

        except Exception as e:
            logger.error("Triage code migration failed")

            metrics = self._get_metrics_from_app(app)
            if metrics:
                logger.info(f"Retrieved metrics despite error: {metrics}")

            return MigrationRunResult(
                success=False,
                error=str(e),
                metrics=metrics,
                mock_logger=mock_logger,
            )

    def run_sqs_event_migration(self, sqs_event: Dict[str, Any]) -> MigrationRunResult:
        """
        Run migration with an SQS event.

        Args:
            sqs_event: SQS event dictionary (raw dict format matching AWS Lambda)

        Returns:
            MigrationRunResult with success status, error, and metrics
        """

        def execute(app: ServiceMigrationApplication) -> None:
            record_count = len(sqs_event.get("Records", []))
            logger.info(f"Running SQS event migration with {record_count} record(s)")

            mock_context = self._create_mock_lambda_context()

            app.handle_sqs_event(sqs_event, mock_context)

        return self._execute_migration(execute, "SQS event")
