"""Helper utilities for running data migration in tests."""
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import unquote, urlparse

from aws_lambda_powertools.utilities.data_classes import SQSEvent
from loguru import logger

from pipeline.application import DataMigrationApplication, DMSEvent
from pipeline.processor import DataMigrationMetrics
from pipeline.utils.config import DatabaseConfig, DataMigrationConfig


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
            workspace: Optional workspace name (defaults to "test")
        """
        self.db_uri = db_uri
        self.dynamodb_endpoint = dynamodb_endpoint
        self.environment = environment
        self.workspace = workspace or "test"

        logger.info("=" * 80)
        logger.info("MigrationHelper initialized with:")
        logger.info(f"  Environment: {self.environment}")
        logger.info(f"  Workspace: {self.workspace}")
        logger.info(f"  DynamoDB Endpoint: {self.dynamodb_endpoint}")
        logger.info("=" * 80)

    def _parse_db_uri(self) -> Dict[str, str]:
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

    def _verify_dynamodb_tables(self, config: DataMigrationConfig) -> None:
        """
        Verify that DynamoDB tables exist and are accessible.

        Args:
            config: Migration configuration with DynamoDB endpoint

        Raises:
            AssertionError: If tables are not accessible
        """
        import boto3

        logger.info("=" * 80)
        logger.info("VERIFYING DYNAMODB TABLES")
        logger.info("=" * 80)

        # Create DynamoDB client with test endpoint and dummy credentials
        dynamodb_client = boto3.client(
            "dynamodb",
            endpoint_url=config.dynamodb_endpoint,
            region_name=os.getenv("AWS_REGION", "eu-west-2"),
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

        # List available tables
        try:
            response = dynamodb_client.list_tables()
            table_names = response.get("TableNames", [])

            logger.info(f"Found {len(table_names)} DynamoDB tables:")
            for table in table_names:
                logger.info(f"  - {table}")
            logger.info("")

            logger.info("Migration will attempt to use tables with pattern:")
            logger.info(f"  {{PROJECT_NAME}}-{config.env}-database-{{resource}}-{config.workspace}")
            logger.info("")

            # Check expected tables
            expected_resources = ["organisation", "location", "healthcare-service"]
            expected_tables = [
                f"ftrs-dos-{config.env}-database-{resource}-{config.workspace}"
                for resource in expected_resources
            ]

            logger.info("Expected tables:")
            for expected in expected_tables:
                exists = expected in table_names
                status = "✓ EXISTS" if exists else "✗ MISSING"
                logger.info(f"  {status}: {expected}")

            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Failed to verify DynamoDB tables: {e}", exc_info=True)
            raise

    def _set_localstack_credentials(self) -> None:
        """
        Set dummy AWS credentials for LocalStack.

        LocalStack doesn't validate credentials but boto3 requires them.
        This sets dummy credentials in the environment for the duration of the test.
        """
        # Store original values to restore later
        self._original_aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        self._original_aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self._original_aws_session_token = os.environ.get("AWS_SESSION_TOKEN")

        # Set dummy credentials for LocalStack
        os.environ["AWS_ACCESS_KEY_ID"] = "test"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
        # Remove session token if present (can cause issues)
        if "AWS_SESSION_TOKEN" in os.environ:
            del os.environ["AWS_SESSION_TOKEN"]

        logger.debug("Set dummy AWS credentials for LocalStack")

    def _restore_aws_credentials(self) -> None:
        """Restore original AWS credentials."""
        if self._original_aws_access_key:
            os.environ["AWS_ACCESS_KEY_ID"] = self._original_aws_access_key
        elif "AWS_ACCESS_KEY_ID" in os.environ:
            del os.environ["AWS_ACCESS_KEY_ID"]

        if self._original_aws_secret_key:
            os.environ["AWS_SECRET_ACCESS_KEY"] = self._original_aws_secret_key
        elif "AWS_SECRET_ACCESS_KEY" in os.environ:
            del os.environ["AWS_SECRET_ACCESS_KEY"]

        if self._original_aws_session_token:
            os.environ["AWS_SESSION_TOKEN"] = self._original_aws_session_token

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

        logger.info("=" * 80)
        logger.info("DataMigrationConfig created:")
        logger.info(f"  Environment: {config.env}")
        logger.info(f"  Workspace: {config.workspace}")
        logger.info(f"  DynamoDB Endpoint: {config.dynamodb_endpoint}")
        logger.info(f"  Database: {db_params['host']}:{db_params['port']}/{db_params['dbname']}")
        logger.info("=" * 80)

        # Verify tables are accessible
        self._verify_dynamodb_tables(config)

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
            # Set LocalStack credentials
            self._set_localstack_credentials()

            config = self.create_migration_config()
            app = DataMigrationApplication(config=config)

            event = DMSEvent(
                type="dms_event",
                record_id=service_id,
                table_name="services",
                method="insert",
            )

            app.handle_dms_event(event)

            metrics = app.processor.metrics if hasattr(app, "processor") else None

            return MigrationRunResult(success=True, application=app, metrics=metrics)

        except Exception as e:
            logger.error("Single service migration failed", exc_info=True)
            return MigrationRunResult(success=False, error=str(e), metrics=None)

        finally:
            # Always restore credentials
            self._restore_aws_credentials()

    def run_full_service_migration(self) -> MigrationRunResult:
        """
        Run full service migration.

        Returns:
            MigrationRunResult with success status, error, and metrics
        """
        try:
            # Set LocalStack credentials
            self._set_localstack_credentials()

            config = self.create_migration_config()
            app = DataMigrationApplication(config=config)

            app.handle_full_sync_event()

            metrics = app.processor.metrics if hasattr(app, "processor") else None

            return MigrationRunResult(success=True, application=app, metrics=metrics)

        except Exception as e:
            logger.error("Full service migration failed", exc_info=True)
            return MigrationRunResult(success=False, error=str(e), metrics=None)

        finally:
            # Always restore credentials
            self._restore_aws_credentials()

    def run_sqs_event_migration(self, sqs_event: Dict[str, Any]) -> MigrationRunResult:
        """
        Run migration with an SQS event.

        Args:
            sqs_event: SQS event dictionary

        Returns:
            MigrationRunResult with success status, error, and metrics
        """
        try:
            # Set LocalStack credentials
            self._set_localstack_credentials()

            logger.info("=" * 80)
            logger.info("MigrationHelper: Starting SQS event migration")
            logger.info("=" * 80)

            # Log event structure
            record_count = len(sqs_event.get("Records", []))
            event_summary = {
                "has_records": "Records" in sqs_event,
                "record_count": record_count,
                "is_empty": len(sqs_event) == 0,
            }
            logger.info(f"Event summary: {event_summary}")
            logger.info(f"SQS event type: {type(sqs_event)}")
            logger.info(f"SQS event keys: {list(sqs_event.keys())}")

            config = self.create_migration_config()
            logger.info("Config created successfully")

            app = DataMigrationApplication(config=config)
            logger.info("DataMigrationApplication instantiated")

            logger.info("Wrapping event in SQSEvent object...")
            sqs_event_obj = SQSEvent(sqs_event)
            logger.info(f"SQSEvent created with {record_count} record(s)")

            logger.info("Calling handle_sqs_event()...")
            app.handle_sqs_event(sqs_event_obj)
            logger.info("handle_sqs_event() completed")

            metrics = None
            if hasattr(app, "processor") and app.processor:
                metrics = app.processor.metrics
                logger.info("Metrics retrieved from app.processor")
            else:
                logger.warning("app.processor not found or is None")

            if metrics:
                logger.info("METRICS CAPTURED:")
                logger.info(f"  Total: {metrics.total_records}")
                logger.info(f"  Supported: {metrics.supported_records}")
                logger.info(f"  Unsupported: {metrics.unsupported_records}")
                logger.info(f"  Transformed: {metrics.transformed_records}")
                logger.info(f"  Migrated: {metrics.migrated_records}")
                logger.info(f"  Skipped: {metrics.skipped_records}")
                logger.info(f"  Errors: {metrics.errors}")
            else:
                logger.error("METRICS ARE NONE!")

            logger.info("=" * 80)
            logger.info("SQS event migration completed")
            logger.info("=" * 80)

            return MigrationRunResult(success=True, application=app, metrics=metrics)

        except Exception as e:
            logger.error("=" * 80)
            logger.error("SQS event migration failed")
            logger.error("=" * 80)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}", exc_info=True)

            import traceback

            logger.error(f"Full traceback:\n{traceback.format_exc()}")

            return MigrationRunResult(success=False, error=str(e), metrics=None)

        finally:
            # Always restore credentials
            self._restore_aws_credentials()
