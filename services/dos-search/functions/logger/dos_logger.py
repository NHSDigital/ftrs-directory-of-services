import os
import time
from functools import cache
from typing import Any, Dict, Literal, Optional

from aws_lambda_powertools.logging import Logger as PowertoolsLogger
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel


class DosLogger:
    """Service-local wrapper that adds DOS structured fields to powertools logs while mirroring the underlying Logger implementation and behaviour.

    Usage:
        f = DosLogger.get(service='dos-search')
        f.info('message', extra_fields=my_extra_fields)

    Behavior:
    - Takes in a log message alongside any other extra fields
    - Calls powertools Logger with `extra=...` so powertools merges it into its JSON output
    """

    def __init__(self, service: str = "dos", debug: bool = False) -> None:
        self.logger = PowertoolsLogger(service=service)
        self.placeholder = (
            "Value not found. Please check if this value was provided in the request."
        )
        self.headers = {}

    # Initialise method handles processing of event details - this should be called at the start of Lambda execution
    def init(self, event: Dict[str, Any]) -> None:
        # Extract of common mandatory fields
        log_data = self.extract(event)
        # Extract of one-time fields for logging below
        details = self.extract_one_time(event)

        # Appends common fields to all subsequent logs
        self.logger.append_keys(**log_data)
        # Log one-time fields from event
        self.info(
            "Logging one-time fields from Request",
            **details,
            dos_message_category="REQUEST",
        )

    @classmethod
    @cache
    def get(cls, service: str = "dos") -> "DosLogger":
        return cls(service=service)

    # --- helper utilities -------------------------------------------------
    def _get_header(self, *names: str) -> Optional[str]:
        # Loops over a list of header keys, returning the first non-empty value found
        for n in names:
            val = self.headers.get(n)
            if val not in (None, ""):
                return val
        return None

    def get_response_size_and_duration(
        self, fhir_resource: FHIRResourceModel, start_time: float
    ) -> tuple[int, int]:
        """Utility to calculate response size in bytes from FHIR resource."""
        duration_ms = int((time.time() - start_time) * 1000)
        try:
            body = fhir_resource.model_dump_json()
            response_size = len(body.encode("utf-8"))
        except Exception:
            response_size = 0
            self.exception(
                "Failed to calculate response size",
                dos_response_time=f"{duration_ms}ms",
                dos_response_size=response_size,
            )
        return response_size, duration_ms

    # --- extract methods -------------------------------------------------
    def extract(self, event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract APIM headers mandatorily appended to all logs into the structured 'mandatory' dict.

        All mandatory fields are present; missing values use the configured placeholder.
        """

        self.headers = event.get("headers") or {}

        mandatory: Dict[str, Any] = {
            "logger": "dos_logger"  # Identifier for when logs are created using our logger
        }

        # Mandatory/default DOS fields
        # NHSD correlation id
        # Client's will provide this header as X-CORRELATION-ID, which will get mapped by the APIM Proxy into the format:
        # <Request-ID>.<Correlation-ID>.<Message-ID>
        # We will therefore extract Correlation ID & Message ID both from the header NHSD-Correlation-ID (Request ID still comes through independently so we will use the separate header for that)
        corr_header = self._get_header(
            "NHSD-Correlation-ID",
        )
        header_length = 3
        reqid_corr_msgid = corr_header.split(".") if corr_header else []
        corr = (
            reqid_corr_msgid[1]
            if len(reqid_corr_msgid) == header_length
            else self.placeholder
        )
        msgid = (
            reqid_corr_msgid[2]
            if len(reqid_corr_msgid) == header_length
            else self.placeholder
        )

        mandatory["dos_nhsd_correlation_id"] = corr

        # APIM message id
        mandatory["dos_message_id"] = msgid

        # NHSD request id
        reqid = (
            self._get_header(
                "NHSD-Request-ID",
            )
            or self.placeholder
        )
        mandatory["dos_nhsd_request_id"] = reqid

        # Default category to LOGGING, can be overridden later
        mandatory["dos_message_category"] = "LOGGING"

        return mandatory

    def extract_one_time(self, event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract APIM headers and common event fields into the structured 'extra' dict.

        One-time logging fields are contained within the 'details' block.
        """
        self.headers = event.get("headers") or {}
        placeholder = self.placeholder

        # One-time fields added to "details" to separate
        details = {}

        api_version = self._get_header("version") or placeholder
        details["dos_search_api_version"] = api_version

        end_user_role = self._get_header("end-user-role") or placeholder
        details["connecting_party_end_user_role"] = end_user_role

        client_id = self._get_header("application-id") or placeholder
        details["connecting_party_application_id"] = client_id

        app_name = self._get_header("application-name") or placeholder
        details["connecting_party_application_name"] = app_name

        # Request params
        req_params: Dict[str, Any] = {}
        query_params = event.get("queryStringParameters") or {}
        path_params = event.get("pathParameters") or {}
        request_context = event.get("requestContext") or {}
        request_context.pop("identity", None)  # Remove identity for privacy/security
        request_context.pop("accountId", None)  # Remove accountId for privacy/security
        req_params["query_params"] = query_params
        req_params["path_params"] = path_params
        req_params["request_context"] = request_context

        details["request_params"] = req_params or {}

        details["dos_environment"] = os.environ.get("ENVIRONMENT") or placeholder

        details["lambda_version"] = (
            os.environ.get("AWS_LAMBDA_FUNCTION_VERSION") or placeholder
        )

        return details

    # --- powertools context -----------------------------------------------
    def append_keys(self, extra: Dict[str, Any]) -> None:
        self.logger.append_keys(**extra)

    def get_keys(self) -> Dict[str, Any]:
        return self.logger.get_current_keys()

    def set_level(self, level: Literal[10, 20, 30, 40, 50]) -> None:
        self.logger.setLevel(level)

    # Manual method to clear ALL appended keys. Not used as setting `clear_state=True` in the Lambda handler should suffice for current logging behaviour
    def clear_state(self) -> None:
        self.logger.clear_state()

    # --- logging methods -----------------------------------------------
    def _log_with_level(
        self,
        level: str,
        message: str,
        **detail: object,
    ) -> None:
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
            log_data["detail"] = detail_map

        # call powertools
        if level == "debug":
            self.logger.debug(message, extra=log_data)
        elif level == "info":
            self.logger.info(message, extra=log_data)
        elif level == "warning":
            self.logger.warning(message, extra=log_data)
        elif level == "error":
            self.logger.error(message, extra=log_data)
        elif level == "exception":
            self.logger.exception(message, extra=log_data)
        else:
            self.logger.info(message, extra=log_data)

    def debug(self, message: str, **detail: object) -> None:
        self._log_with_level("debug", message, **detail)

    def info(self, message: str, **detail: object) -> None:
        self._log_with_level("info", message, **detail)

    def warning(self, message: str, **detail: object) -> None:
        self._log_with_level("warning", message, **detail)

    def error(self, message: str, **detail: object) -> None:
        self._log_with_level("error", message, **detail)

    def exception(self, message: str, **detail: object) -> None:
        self._log_with_level("exception", message, **detail)
