"""Lambda invocation abstraction for local and AWS testing.

This module provides a unified interface for invoking Lambda functions,
supporting both:
1. Real AWS Lambda invocation
2. Direct Lambda handler invocation (for local testing)
"""

import importlib
import importlib.util
import json
import os
import sys
import types
from typing import Any, Callable, Optional

from utilities.infra.lambda_util import LambdaWrapper
from utilities.testcontainers.fixtures import is_local_test_mode


class MockLambdaContext:
    """Mock Lambda context for local testing."""

    def __init__(self, function_name: str = "test-function"):
        self.function_name = function_name
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = f"test-function-arn-{function_name}"
        self.aws_request_id = "test-request-id"
        self.log_group_name = f"/aws/lambda/{function_name}"
        self.log_stream_name = "test-log-stream"


class LambdaInvoker:
    """Unified Lambda invoker for both AWS and local testing.

    In AWS mode, this invokes Lambda functions directly via AWS Lambda API.
    In local mode, this calls Lambda handler functions directly (no server needed).
    """

    def __init__(
        self,
        lambda_wrapper: Optional[LambdaWrapper] = None,
        endpoint_url: Optional[str] = None,
        use_direct_invocation: bool = True,
    ):
        """Initialize the invoker.

        Args:
            lambda_wrapper: LambdaWrapper for AWS Lambda invocation
            endpoint_url: LocalStack endpoint URL (for DynamoDB, etc.)
            use_direct_invocation: If True, call Lambda handlers directly in local mode
        """
        self._lambda_wrapper = lambda_wrapper
        self._endpoint_url = endpoint_url
        self._is_local = is_local_test_mode()
        self._use_direct_invocation = use_direct_invocation
        self._handlers: dict[str, Callable] = {}

    @property
    def is_local_mode(self) -> bool:
        """Check if running in local mode."""
        return self._is_local

    def check_function_exists(self, function_name: str) -> bool:
        """Check if a function exists.

        In local mode, always returns True (we'll try to load the handler).
        In AWS mode, checks via AWS Lambda API.

        Args:
            function_name: Lambda function name

        Returns:
            True if function exists or in local mode
        """
        if self._is_local:
            # In local mode, try to load the handler
            return self._get_handler_for_function(function_name) is not None
        else:
            return self._lambda_wrapper.check_function_exists(function_name)

    def invoke_function(
        self,
        function_name: str,
        event: dict[str, Any],
    ) -> dict[str, Any]:
        """Invoke a Lambda function.

        In local mode, calls the handler function directly.
        In AWS mode, invokes via AWS Lambda API.

        Args:
            function_name: Lambda function name
            event: Lambda event (API Gateway format)

        Returns:
            Response (API Gateway response format)
        """
        if self._is_local and self._use_direct_invocation:
            return self._invoke_direct(function_name, event)
        else:
            return self._lambda_wrapper.invoke_function(function_name, event)

    def _get_handler_for_function(self, function_name: str) -> Optional[Callable]:
        """Get the Lambda handler function for a given function name.

        Maps function names to their handlers based on naming convention.

        Args:
            function_name: Lambda function name (e.g., "ftrs-dos-local-dos-search-ods-code-lambda-test")

        Returns:
            Handler function or None if not found
        """
        if function_name in self._handlers:
            return self._handlers[function_name]

        # Disable X-Ray tracing before importing handlers
        os.environ["AWS_XRAY_SDK_ENABLED"] = "false"
        os.environ["POWERTOOLS_TRACE_DISABLED"] = "true"

        # Map function names to handlers
        # The function name pattern is: {project}-{env}-{stack}-{resource}-{workspace}
        # e.g., ftrs-dos-local-dos-search-ods-code-lambda-test
        try:
            if "dos-search-ods-code" in function_name:
                self._ensure_xray_sdk_available()

                # Add dos-search service path and its venv to sys.path
                dos_search_path = self._get_dos_search_path()
                dos_search_venv = os.path.join(
                    dos_search_path, ".venv", "lib", "python3.13", "site-packages"
                )

                # Also try python3.12 if 3.13 doesn't exist
                if not os.path.exists(dos_search_venv):
                    dos_search_venv = os.path.join(
                        dos_search_path, ".venv", "lib", "python3.12", "site-packages"
                    )

                # Insert the venv site-packages first so it takes precedence
                if dos_search_venv not in sys.path and os.path.exists(dos_search_venv):
                    sys.path.insert(0, dos_search_venv)
                if dos_search_path not in sys.path:
                    sys.path.insert(0, dos_search_path)

                module = importlib.import_module(
                    "functions.dos_search_ods_code_function"
                )
                lambda_handler = getattr(module, "lambda_handler")

                self._handlers[function_name] = lambda_handler
                return lambda_handler

            # Add more handlers here as needed
            # elif "crud-api" in function_name:
            #     from services.crud_apis...

        except ImportError as e:
            print(f"Warning: Could not import handler for {function_name}: {e}")
            return None

        return None

    @staticmethod
    def _ensure_xray_sdk_available() -> None:
        """Ensure aws_xray_sdk is importable.

        The dos-search Lambda uses AWS Lambda Powertools Tracer, which may
        import `aws_xray_sdk` at module import time. The service_automation
        environment used in CI doesn't necessarily include aws_xray_sdk.

        In local test mode we disable tracing; providing a minimal stub keeps
        imports working without changing the runtime behavior.
        """

        if importlib.util.find_spec("aws_xray_sdk") is not None:
            return

        if "aws_xray_sdk" in sys.modules:
            return

        aws_xray_sdk = types.ModuleType("aws_xray_sdk")
        aws_xray_sdk.__dict__["__all__"] = ["global_sdk_config", "core"]

        class _GlobalSdkConfig:
            @staticmethod
            def set_sdk_enabled(_enabled: bool) -> None:  # noqa: ARG004
                return

        aws_xray_sdk.global_sdk_config = _GlobalSdkConfig()  # type: ignore[attr-defined]

        aws_xray_sdk_core = types.ModuleType("aws_xray_sdk.core")

        class _DummySubsegment:
            def put_metadata(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                return

            def put_annotation(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                return

        class _XRayRecorder:
            def in_subsegment(self, *args: Any, **kwargs: Any):  # noqa: ANN201,ARG002
                class _Ctx:
                    def __enter__(self) -> _DummySubsegment:
                        return _DummySubsegment()

                    def __exit__(
                        self,
                        exc_type: object,
                        exc: object,
                        tb: object,
                    ) -> bool:
                        return False

                return _Ctx()

            def in_segment(self, *args: Any, **kwargs: Any):  # noqa: ANN201,ARG002
                class _Ctx:
                    def __enter__(self) -> _DummySubsegment:
                        return _DummySubsegment()

                    def __exit__(
                        self,
                        exc_type: object,
                        exc: object,
                        tb: object,
                    ) -> bool:
                        return False

                return _Ctx()

            def configure(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                return

            def begin_segment(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                return

            def end_segment(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                return

            def begin_subsegment(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                return

            def end_subsegment(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                return

            def current_segment(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                return None

            def current_subsegment(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                return None

        aws_xray_sdk_core.xray_recorder = _XRayRecorder()  # type: ignore[attr-defined]

        def _noop(*args: Any, **kwargs: Any) -> None:  # noqa: ARG001,ARG002
            return

        aws_xray_sdk_core.patch = _noop  # type: ignore[attr-defined]
        aws_xray_sdk_core.patch_all = _noop  # type: ignore[attr-defined]

        aws_xray_sdk.core = aws_xray_sdk_core  # type: ignore[attr-defined]

        sys.modules["aws_xray_sdk"] = aws_xray_sdk
        sys.modules["aws_xray_sdk.core"] = aws_xray_sdk_core

        # Optional extension module used by powertools for ignored URLs
        aws_xray_sdk_ext = types.ModuleType("aws_xray_sdk.ext")
        aws_xray_sdk_ext_httplib = types.ModuleType("aws_xray_sdk.ext.httplib")
        aws_xray_sdk_ext_httplib.add_ignored = _noop  # type: ignore[attr-defined]
        sys.modules["aws_xray_sdk.ext"] = aws_xray_sdk_ext
        sys.modules["aws_xray_sdk.ext.httplib"] = aws_xray_sdk_ext_httplib

    def _get_dos_search_path(self) -> str:
        """Get the path to the dos-search service."""
        # Navigate from tests/service_automation/tests/utilities/infra to services/dos-search
        current_dir = os.path.dirname(__file__)
        repo_root = os.path.abspath(
            os.path.join(current_dir, "..", "..", "..", "..", "..")
        )
        return os.path.join(repo_root, "services", "dos-search")

    def _invoke_direct(
        self,
        function_name: str,
        event: dict[str, Any],
    ) -> dict[str, Any]:
        """Call Lambda handler directly.

        Args:
            function_name: Lambda function name
            event: Lambda event

        Returns:
            Handler response
        """
        handler = self._get_handler_for_function(function_name)

        if handler is None:
            return {
                "statusCode": 500,
                "headers": {},
                "body": json.dumps({"error": f"Handler not found for {function_name}"}),
            }

        try:
            context = MockLambdaContext(function_name)
            result = handler(event, context)
            return result
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {},
                "body": json.dumps({"error": str(e)}),
            }
