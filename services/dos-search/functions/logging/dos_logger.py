import logging
import os
from typing import Any, Dict, Optional

from aws_lambda_powertools.logging import Logger as PowertoolsLogger


class DosLogger:
    """Service-local wrapper that adds DOS structured fields to powertools logs.

    Usage:
        f = DosLogger(service='dos-search')
        f.info('message', event=my_event)

    Behavior:
    - Takes in a log_data field alongside any other extra fields
    - Calls powertools Logger with `extra=...` so powertools merges it into its JSON output
    - Optionally prints a debug preview when debug=True
    - Placeholder for missing values is configurable via ENV `DOS_LOG_PLACEHOLDER` (default 'TBC').
        If set to 'NULL' the wrapper will emit Python None (JSON null) for missing values.
    TODO: Add logic to persist last logged fields for future calls if log_data is not provided
    """

    def __init__(self, service: str = "dos", debug: bool = False) -> None:
        self._logger = PowertoolsLogger(service=service)
        self._service = service
        self.debug = debug
        self.placeholder = "DOS_LOG_PLACEHOLDER"
        self.headers = dict()

    # --- helper utilities -------------------------------------------------
    def _get_header(self, *names: str) -> str:
        hdr_lower = {k.lower(): v for k, v in self.headers.items()}
        # try original casing keys first, then lowercased mapping
        for n in names:
            val = self.headers.get(n)
            if val not in (None, ""):
                return val
        # fallback to lowercased lookup of provided names
        for n in names:
            val = hdr_lower.get(n.lower())
            if val not in (None, ""):
                return val
        return self.placeholder

    # --- extract methods -------------------------------------------------
    def extract(self, event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract APIM headers and common event fields into the structured 'extra' dict.

        All mandatory fields are present; missing values use the configured placeholder.
        Optional one-time fields are prefixed with 'Opt_'.

        Extracts are handled here as passing the entire event object to the handler presents issues for the pytest library mocks.
        """

        self.headers = event.get("headers") or {}

        mandatory: Dict[str, Any] = {
            "logger": "dos_logger"  # Identifier for when logs are created using our logger
        }

        # Mandatory/default DOS fields
        # NHSD correlation id
        corr = self._get_header("NHSD-Correlation-ID", "NHSD-Request-Id")
        mandatory["dos_nhsd_correlation_id"] = corr

        # NHSD request id
        reqid = self._get_header("NHSD-Request-ID")
        mandatory["dos_nhsd_request_id"] = reqid

        # APIM message id
        msgid = self._get_header(
            "x-apim-msg-id", "X-Message-Id", "apim-message-id", "dos-message-id"
        )
        mandatory["dos_message_id"] = msgid

        # Default category to LOGGING, can be overridden later
        mandatory["dos_message_category"] = "LOGGING"

        return mandatory

    def extract_one_time(self, event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        self.headers = event.get("headers") or {}
        placeholder = self.placeholder

        # One-time fields added to "details" to separate
        details = {}

        end_user_role = self._get_header("NHSD-End-User-Role")
        details["opt_dos_end_user_role"] = end_user_role

        client_id = self._get_header("NHSD-Client-Id")
        details["opt_dos_client_id"] = client_id

        app_name = self._get_header("NHSD-Connecting-Party-App-Name")
        details["opt_dos_application_name"] = app_name

        # Request params (queryStringParameters + pathParameters)
        req_params: Dict[str, Any] = {}
        query_params = (
            event.get("queryStringParameters")
            or event.get("query_string_parameters")
            or {}
        )
        path_params = event.get("pathParameters") or event.get("path_parameters") or {}
        request_context = (
            event.get("requestContext") or event.get("request_context") or {}
        )
        req_params["query_params"] = query_params
        req_params["path_params"] = path_params
        req_params["request_context"] = request_context

        details["opt_dos_request_params"] = req_params or {}

        details["opt_dos_response_time"] = placeholder

        details["opt_dos_environment"] = (
            os.environ.get("ENVIRONMENT") or os.environ.get("WORKSPACE") or placeholder
        )

        details["opt_dos_api_version"] = (
            self._get_header("x-api-version", "api-version") or placeholder
        )

        details["opt_dos_lambda_version"] = (
            os.environ.get("AWS_LAMBDA_FUNCTION_VERSION") or placeholder
        )

        details["opt_dos_response_size"] = placeholder

        return details

    # --- powertools context -----------------------------------------------
    def append_keys(self, extra: Dict[str, Any]) -> None:
        self._logger.append_keys(**extra)

    # Manual method to clear ALL appended keys. Not used as setting `clear_state=True` in the Lambda handler should suffice for current logging behaviour
    def clear_state(self) -> None:
        self._logger.clear_state()

    # --- logging methods -----------------------------------------------
    def _log_with_level(
        self,
        level: str,
        message: str,
        **detail: object,
    ) -> Dict[str, Any]:
        # Handles deliberately passed None values
        log_data = {}
        # convert detail (kwargs) to dict for manipulation
        detail_map = dict(detail) if detail else {}

        # Allow certain dos_* fields to be provided as top-level overrides
        override_keys = {
            "dos_message_category",
        }
        if detail_map:
            for k in list(detail_map.keys()):
                if k in override_keys:
                    log_data[k] = detail_map.pop(k)
            if detail_map:
                log_data["detail"] = detail_map

        # call powertools
        try:
            if level == "info":
                self._logger.info(message, extra=log_data)
            elif level == "warning":
                self._logger.warning(message, extra=log_data)
            elif level == "error":
                self._logger.error(message, extra=log_data)
            elif level == "exception":
                self._logger.exception(message, extra=log_data)
            else:
                self._logger.info(message, extra=log_data)
        except TypeError:
            base_logger = logging.getLogger(self._service)
            (base_logger.info(message),)
        return log_data

    def info(self, message: str, **detail: object) -> Dict[str, Any]:
        log_data = self._log_with_level("info", message, **detail)
        return log_data

    def warning(self, message: str, **detail: object) -> Dict[str, Any]:
        log_data = self._log_with_level("warning", message, **detail)
        return log_data

    def error(self, message: str, **detail: object) -> Dict[str, Any]:
        log_data = self._log_with_level("error", message, **detail)
        return log_data

    def exception(self, message: str, **detail: object) -> Dict[str, Any]:
        log_data = self._log_with_level("exception", message, **detail)
        return log_data


# Instantiate logger here to allow import to sub-directories
service = "dos-search"
dos_logger = DosLogger(service=service)
