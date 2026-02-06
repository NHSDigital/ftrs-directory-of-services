"""ETL ODS Pipeline Invoker for local testing.

This module provides utilities to run the complete ETL ODS pipeline locally
by invoking Lambda handlers directly and managing SQS queue message flow.
"""

import json
import os
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import boto3
from loguru import logger
from utilities.local.lambda_invoker import LambdaInvoker
from utilities.test_keys import get_test_private_key


@dataclass
class PipelineResult:
    """Result of a pipeline execution."""

    extractor_result: dict[str, Any]
    transformer_results: list[dict[str, Any]]
    consumer_results: list[dict[str, Any]]
    messages_processed: int
    errors: list[str]


class ETLOdsPipelineInvoker:
    """Invoke the complete ETL ODS pipeline locally.

    This class orchestrates the three-stage ETL ODS pipeline:
    1. Extractor: Fetches organizations from ODS API and sends to transform queue
    2. Transformer: Transforms FHIR data and sends to consumer queue
    3. Consumer: Sends updates to APIM API

    For local testing, it can either:
    - Use real SQS queues in LocalStack
    - Capture messages in-memory and pass them between stages

    Example:
        invoker = ETLOdsPipelineInvoker(
            endpoint_url="http://localhost:4566",
            ods_mock_url="http://localhost:8003/fhir/Organization",
            apim_url="http://localhost:8001",
        )
        result = invoker.run_full_pipeline("2025-12-08")
    """

    def __init__(
        self,
        endpoint_url: str,
        ods_mock_url: str,
        apim_url: str,
        etl_ods_path: Optional[str] = None,
        use_real_queues: bool = True,
    ):
        """Initialize the ETL ODS pipeline invoker.

        Args:
            endpoint_url: LocalStack endpoint URL for AWS services
            ods_mock_url: URL of the ODS mock server
            apim_url: URL of the local APIM/CRUD APIs server
            etl_ods_path: Path to the ETL ODS service directory
            use_real_queues: If True, use LocalStack SQS; if False, capture in-memory
        """
        self.endpoint_url = endpoint_url
        self.ods_mock_url = ods_mock_url
        self.apim_url = apim_url
        self.use_real_queues = use_real_queues

        # Default path to ETL ODS service
        # Path traversal: etl_ods_invoker.py -> local -> utilities -> tests -> service_automation -> tests -> ftrs-directory-of-services
        if etl_ods_path is None:
            repo_root = Path(__file__).parent.parent.parent.parent.parent.parent
            etl_ods_path = repo_root / "services" / "etl-ods"
        self.etl_ods_path = Path(etl_ods_path)

        # Environment variables for the pipeline
        self.env_vars = self._build_env_vars()

        # Add ETL ODS path to sys.path
        if str(self.etl_ods_path) not in sys.path:
            sys.path.insert(0, str(self.etl_ods_path))

    def _build_env_vars(self) -> dict[str, str]:
        """Build environment variables for the pipeline."""
        # RSA private key for JWT signing (generated at runtime for testing)
        test_private_key = os.environ.get("LOCAL_PRIVATE_KEY") or get_test_private_key()

        return {
            "ENVIRONMENT": os.environ.get("ENVIRONMENT", "local"),
            "WORKSPACE": os.environ.get("WORKSPACE", "test"),
            "PROJECT_NAME": os.environ.get("PROJECT_NAME", "ftrs-dos"),
            "AWS_REGION": os.environ.get("AWS_REGION", "eu-west-2"),
            "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION", "eu-west-2"),
            "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
            "AWS_ENDPOINT_URL": self.endpoint_url,
            "ENDPOINT_URL": self.endpoint_url,
            "LOCAL_ODS_URL": self.ods_mock_url,
            "LOCAL_APIM_API_URL": self.apim_url,
            "ODS_API_PAGE_LIMIT": "100",
            "MAX_RECEIVE_COUNT": "3",
            # JWT authentication for local testing
            "LOCAL_PRIVATE_KEY": test_private_key,
            "LOCAL_KID": os.environ.get("LOCAL_KID", "test-kid-local"),
            "LOCAL_TOKEN_URL": os.environ.get(
                "LOCAL_TOKEN_URL", f"{self.apim_url}/oauth2/token"
            ),
            # Disable X-Ray tracing
            "AWS_XRAY_SDK_ENABLED": "false",
            "POWERTOOLS_TRACE_DISABLED": "true",
        }

    def run_full_pipeline(
        self,
        date: str,
        correlation_id: Optional[str] = None,
    ) -> PipelineResult:
        """Run the complete ETL ODS pipeline.

        Args:
            date: The date to process (format: YYYY-MM-DD)
            correlation_id: Optional correlation ID for tracing

        Returns:
            PipelineResult with results from all stages
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        errors = []
        transformer_results = []
        consumer_results = []

        # Set environment variables
        self._set_env_vars()

        try:
            # Purge queues to ensure clean state
            self._purge_queues()

            # 1. Run extractor
            logger.info(f"Running extractor for date: {date}")
            extractor_result = self._run_extractor(date, correlation_id)

            if extractor_result.get("statusCode") != 200:
                errors.append(f"Extractor failed: {extractor_result}")
                return PipelineResult(
                    extractor_result=extractor_result,
                    transformer_results=[],
                    consumer_results=[],
                    messages_processed=0,
                    errors=errors,
                )

            # 2. Process transformer queue
            if self.use_real_queues:
                transform_messages = self._read_queue_messages("transform-queue")
            else:
                # In-memory mode would capture messages differently
                transform_messages = []

            logger.info(f"Processing {len(transform_messages)} transform messages")
            for batch in self._batch_messages(transform_messages, 10):
                result = self._run_transformer(batch)
                transformer_results.append(result)

            # 3. Process consumer queue
            if self.use_real_queues:
                consumer_messages = self._read_queue_messages("queue")
            else:
                consumer_messages = []

            logger.info(f"Processing {len(consumer_messages)} consumer messages")
            for batch in self._batch_messages(consumer_messages, 10):
                result = self._run_consumer(batch)
                consumer_results.append(result)

            return PipelineResult(
                extractor_result=extractor_result,
                transformer_results=transformer_results,
                consumer_results=consumer_results,
                messages_processed=len(transform_messages),
                errors=errors,
            )

        finally:
            self._restore_env_vars()

    def run_extractor_only(
        self,
        date: str,
        correlation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Run only the extractor stage.

        Args:
            date: The date to process
            correlation_id: Optional correlation ID

        Returns:
            Extractor Lambda response
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        self._set_env_vars()
        try:
            return self._run_extractor(date, correlation_id)
        finally:
            self._restore_env_vars()

    def _run_extractor(self, date: str, correlation_id: str) -> dict[str, Any]:
        """Run the extractor Lambda handler."""
        invoker = LambdaInvoker(
            handler_path=str(self.etl_ods_path),
            handler_module="extractor.extractor",
            handler_function="extractor_lambda_handler",
            env_vars=self.env_vars,
        )

        event = {
            "date": date,
            "headers": {"X-Correlation-ID": correlation_id},
        }

        return invoker.invoke(event)

    def _run_transformer(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """Run the transformer Lambda handler with SQS messages."""
        invoker = LambdaInvoker(
            handler_path=str(self.etl_ods_path),
            handler_module="transformer.transformer",
            handler_function="transformer_lambda_handler",
            env_vars=self.env_vars,
        )

        return invoker.invoke_with_sqs_event(messages)

    def _run_consumer(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """Run the consumer Lambda handler with SQS messages."""
        invoker = LambdaInvoker(
            handler_path=str(self.etl_ods_path),
            handler_module="consumer.consumer",
            handler_function="consumer_lambda_handler",
            env_vars=self.env_vars,
        )

        return invoker.invoke_with_sqs_event(messages)

    def _purge_queues(self) -> None:
        """Purge all ETL ODS queues to ensure clean state before running pipeline."""
        sqs = boto3.client(
            "sqs",
            endpoint_url=self.endpoint_url,
            region_name="eu-west-2",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

        env = self.env_vars.get("ENVIRONMENT", "local")
        workspace = self.env_vars.get("WORKSPACE", "test")
        project = self.env_vars.get("PROJECT_NAME", "ftrs-dos")

        queue_suffixes = ["extraction-queue", "transform-queue", "load-queue", "queue"]

        for suffix in queue_suffixes:
            queue_name = f"{project}-{env}-etl-ods-{suffix}"
            if workspace:
                queue_name = f"{queue_name}-{workspace}"

            try:
                response = sqs.get_queue_url(QueueName=queue_name)
                queue_url = response["QueueUrl"]
                sqs.purge_queue(QueueUrl=queue_url)
                logger.info(f"Purged queue: {queue_name}")
            except Exception as e:
                logger.debug(f"Could not purge queue {queue_name}: {e}")

    def _read_queue_messages(
        self,
        queue_suffix: str,
        max_messages: int = 100,
        wait_time: int = 2,
    ) -> list[dict[str, Any]]:
        """Read messages from an SQS queue.

        Args:
            queue_suffix: Queue suffix (e.g., "transform-queue", "queue")
            max_messages: Maximum number of messages to read
            wait_time: Wait time in seconds for long polling

        Returns:
            List of message bodies
        """
        sqs = boto3.client(
            "sqs",
            endpoint_url=self.endpoint_url,
            region_name="eu-west-2",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

        env = self.env_vars.get("ENVIRONMENT", "local")
        workspace = self.env_vars.get("WORKSPACE", "test")
        project = self.env_vars.get("PROJECT_NAME", "ftrs-dos")

        queue_name = f"{project}-{env}-etl-ods-{queue_suffix}"
        if workspace:
            queue_name = f"{queue_name}-{workspace}"

        try:
            response = sqs.get_queue_url(QueueName=queue_name)
            queue_url = response["QueueUrl"]
        except Exception as e:
            logger.warning(f"Could not get queue URL for {queue_name}: {e}")
            return []

        messages = []
        while len(messages) < max_messages:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=min(10, max_messages - len(messages)),
                WaitTimeSeconds=wait_time,
                AttributeNames=["All"],
            )

            batch = response.get("Messages", [])
            if not batch:
                break

            for msg in batch:
                try:
                    body = json.loads(msg["Body"])
                    messages.append(body)
                    # Delete the message after reading
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg["ReceiptHandle"],
                    )
                except json.JSONDecodeError:
                    messages.append({"body": msg["Body"]})

        logger.debug(f"Read {len(messages)} messages from {queue_name}")
        return messages

    def _batch_messages(
        self,
        messages: list[dict[str, Any]],
        batch_size: int = 10,
    ) -> list[list[dict[str, Any]]]:
        """Split messages into batches.

        Args:
            messages: List of messages
            batch_size: Maximum batch size

        Returns:
            List of message batches
        """
        for i in range(0, len(messages), batch_size):
            yield messages[i : i + batch_size]

    def _set_env_vars(self) -> None:
        """Set environment variables for the pipeline."""
        self._original_env = {}
        for key, value in self.env_vars.items():
            self._original_env[key] = os.environ.get(key)
            os.environ[key] = value

    def _restore_env_vars(self) -> None:
        """Restore original environment variables."""
        for key, value in self._original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
