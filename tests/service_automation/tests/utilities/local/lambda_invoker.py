"""Direct Lambda handler invocation for local testing.

This module provides utilities to invoke Lambda handlers directly
without requiring AWS Lambda service or LocalStack Pro.
"""

import json
import os
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from loguru import logger


@dataclass
class MockLambdaContext:
    """Mock AWS Lambda context for local testing."""

    function_name: str = "local-test-function"
    function_version: str = "$LATEST"
    invoked_function_arn: str = "test-function-arn-local-test-function"
    memory_limit_in_mb: int = 128
    aws_request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    log_group_name: str = "/aws/lambda/local-test-function"
    log_stream_name: str = "test-log-stream"
    identity: Any = None
    client_context: Any = None

    def get_remaining_time_in_millis(self) -> int:
        """Return remaining time in milliseconds (mock value)."""
        return 300000  # 5 minutes


class LambdaInvoker:
    """Invoke Lambda handlers directly for local testing.

    This class allows invoking Lambda handlers as Python functions,
    bypassing the need for AWS Lambda service.

    Example:
        invoker = LambdaInvoker(
            handler_path="/path/to/service",
            handler_module="functions.my_handler",
            handler_function="lambda_handler",
        )
        result = invoker.invoke({"key": "value"})
    """

    def __init__(
        self,
        handler_path: str,
        handler_module: str,
        handler_function: str = "lambda_handler",
        env_vars: Optional[dict[str, str]] = None,
    ):
        """Initialize the Lambda invoker.

        Args:
            handler_path: Path to the Lambda service directory
            handler_module: Module path to the handler (e.g., "functions.my_handler")
            handler_function: Name of the handler function (default: "lambda_handler")
            env_vars: Environment variables to set before invoking
        """
        self.handler_path = Path(handler_path)
        self.handler_module = handler_module
        self.handler_function = handler_function
        self.env_vars = env_vars or {}
        self._handler: Optional[Callable] = None

    def _load_handler(self) -> Callable:
        """Load the Lambda handler function."""
        if self._handler is not None:
            return self._handler

        # Add handler path to sys.path
        handler_path_str = str(self.handler_path)
        if handler_path_str not in sys.path:
            sys.path.insert(0, handler_path_str)

        # Clear any cached 'common' modules to avoid conflicts between services
        # (e.g., data-migration/common vs etl-ods/common)
        common_modules = [
            key for key in sys.modules if key == "common" or key.startswith("common.")
        ]
        for mod in common_modules:
            del sys.modules[mod]

        # Import the module and get the handler function
        try:
            module = __import__(self.handler_module, fromlist=[self.handler_function])
            self._handler = getattr(module, self.handler_function)
            logger.debug(
                f"Loaded handler: {self.handler_module}.{self.handler_function}"
            )
            return self._handler
        except Exception as e:
            logger.error(f"Failed to load handler from {handler_path_str}: {e}")
            raise

    def invoke(
        self,
        event: dict[str, Any],
        context: Optional[MockLambdaContext] = None,
    ) -> dict[str, Any]:
        """Invoke the Lambda handler with the given event.

        Args:
            event: The Lambda event payload
            context: Optional Lambda context (uses MockLambdaContext if not provided)

        Returns:
            The handler response
        """
        # Set environment variables
        original_env = {}
        for key, value in self.env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            handler = self._load_handler()
            ctx = context or MockLambdaContext()
            result = handler(event, ctx)
            return result
        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def invoke_with_sqs_event(
        self,
        messages: list[dict[str, Any]],
        context: Optional[MockLambdaContext] = None,
    ) -> dict[str, Any]:
        """Invoke the Lambda handler with SQS event format.

        Args:
            messages: List of message bodies to wrap in SQS Records format
            context: Optional Lambda context

        Returns:
            The handler response
        """
        sqs_event = self._build_sqs_event(messages)
        return self.invoke(sqs_event, context)

    def _build_sqs_event(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """Build an SQS event from message bodies.

        Args:
            messages: List of message bodies

        Returns:
            SQS event in Lambda format
        """
        records = []
        for i, msg in enumerate(messages):
            record = {
                "messageId": str(uuid.uuid4()),
                "receiptHandle": f"receipt-handle-{i}",
                "body": json.dumps(msg) if isinstance(msg, dict) else msg,
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1234567890",
                    "SenderId": "test-sender",
                    "ApproximateFirstReceiveTimestamp": "1234567890",
                },
                "messageAttributes": {},
                "md5OfBody": "test-md5",
                "eventSource": "aws:sqs",
                "eventSourceARN": "test-sqs-queue-arn",
                "awsRegion": "eu-west-2",
            }
            records.append(record)

        return {"Records": records}
