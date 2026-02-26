import os
import time
from functools import cache
from typing import Any, Literal, Optional

from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import fetch_or_set_correlation_id
from ftrs_common.utils.request_id import fetch_or_set_request_id

from functions.logbase import DosSearchLogBase

PLACEHOLDER = "Value not found. Please check if this value was provided in the request."


class DosLogger:
    """Service-local utility class that handles DOS-specific header extraction,
    request/correlation ID setup, and response metrics calculation.

    Logging is performed via the FTRS common Logger directly at call sites.

    Usage:
        dos_logger = DosLogger.get(service='dos-search')
        logger = Logger.get(service='dos-search')
        dos_logger.init(event)
        logger.log(DosSearchLogBase.DOS_SEARCH_002, ods_code=ods_code)
    """

    def __init__(self, service: str = "dos") -> None:
        self.logger = Logger.get(service=service)
        self.headers = {}

    # Initialise method handles processing of event details - this should be called at the start of Lambda execution
    def init(self, event: dict[str, Any]) -> None:
        # Extract of common mandatory fields
        log_data = self.extract(event)
        # Extract of one-time fields for logging below
        details = self.extract_one_time(event)

        # Set request and correlation IDs for the common logger
        fetch_or_set_request_id(header_id=self._get_header("nhsd-request-id"))
        fetch_or_set_correlation_id(existing=self._get_header("nhsd-correlation-id"))

        # Appends common DOS fields to all subsequent logs
        self.logger.append_keys(**log_data)
        # Log one-time fields from event via the common logger
        self.logger.log(
            DosSearchLogBase.DOS_SEARCH_001,
            **details,
            dos_message_category="REQUEST",
        )

    @classmethod
    @cache
    def get(cls, service: str = "dos") -> "DosLogger":
        return cls(service=service)

    # --- helper utilities -------------------------------------------------
    def set_headers(self, headers: dict[str, Any]) -> None:
        """Set headers with keys converted to lowercase."""
        self.headers = {k.lower(): v for k, v in headers.items()}

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
            self.logger.log(
                DosSearchLogBase.DOS_SEARCH_010,
                dos_response_time=f"{duration_ms}ms",
                dos_response_size=response_size,
            )
        return response_size, duration_ms

    # --- extract methods -------------------------------------------------
    def extract(self, event: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Extract APIM headers mandatorily appended to all logs into the structured 'mandatory' dict.

        All mandatory fields are present; missing values use the configured placeholder.
        """

        self.set_headers(event.get("headers") or {})

        mandatory: dict[str, Any] = {
            "logger": "dos_logger"  # Identifier for when logs are created using our logger
        }

        # Mandatory/default DOS fields
        # NHSD correlation id
        # Client's will provide this header as X-CORRELATION-ID, which will get mapped by the APIM Proxy into the format:
        # <Request-ID>.<Correlation-ID>.<Message-ID>
        # We will therefore extract Correlation ID & Message ID both from the header NHSD-Correlation-ID (Request ID still comes through independently so we will use the separate header for that)
        corr_header = self._get_header(
            "nhsd-correlation-id",
        )

        reqid_corr_msgid = corr_header.split(".") if corr_header else []

        correlation_id_index = 1
        message_id_index = 2

        correlation_id = PLACEHOLDER
        message_id = PLACEHOLDER

        if len(reqid_corr_msgid) > correlation_id_index:
            correlation_id = reqid_corr_msgid[correlation_id_index] or PLACEHOLDER
        if len(reqid_corr_msgid) > message_id_index:
            message_id = reqid_corr_msgid[message_id_index] or PLACEHOLDER

        mandatory["dos_nhsd_correlation_id"] = correlation_id
        mandatory["dos_message_id"] = message_id

        # NHSD request id
        mandatory["dos_nhsd_request_id"] = (
            self._get_header("nhsd-request-id") or PLACEHOLDER
        )

        # Default category to LOGGING, can be overridden later
        mandatory["dos_message_category"] = "LOGGING"

        return mandatory

    def extract_one_time(self, event: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Extract APIM headers and common event fields into the structured 'extra' dict.

        One-time logging fields are contained within the 'details' block.
        """
        self.set_headers(event.get("headers") or {})

        # One-time fields added to "details" to separate
        details = {}

        api_version = self._get_header("version") or PLACEHOLDER
        details["dos_search_api_version"] = api_version

        end_user_role = self._get_header("end-user-role") or PLACEHOLDER
        details["connecting_party_end_user_role"] = end_user_role

        client_id = self._get_header("application-id") or PLACEHOLDER
        details["connecting_party_application_id"] = client_id

        app_name = self._get_header("application-name") or PLACEHOLDER
        details["connecting_party_application_name"] = app_name

        # Request params
        req_params: dict[str, Any] = {}
        query_params = event.get("queryStringParameters") or {}
        path_params = event.get("pathParameters") or {}
        request_context = event.get("requestContext") or {}
        request_context.pop("identity", "None")  # Remove identity for privacy/security
        request_context.pop(
            "accountId", "None"
        )  # Remove accountId for privacy/security
        req_params["query_params"] = query_params
        req_params["path_params"] = path_params
        req_params["request_context"] = request_context

        details["request_params"] = req_params or {}

        details["dos_environment"] = os.environ.get("ENVIRONMENT") or PLACEHOLDER

        details["lambda_version"] = (
            os.environ.get("AWS_LAMBDA_FUNCTION_VERSION") or PLACEHOLDER
        )

        return details

    # --- powertools context -----------------------------------------------
    def append_keys(self, extra: dict[str, Any]) -> None:
        self.logger.append_keys(**extra)

    def get_keys(self) -> dict[str, Any]:
        return self.logger.get_current_keys()

    def set_level(self, level: Literal[10, 20, 30, 40, 50]) -> None:
        self.logger.setLevel(level)

    # Manual method to clear ALL appended keys. Not used as setting `clear_state=True` in the Lambda handler should suffice for current logging behaviour
    def clear_state(self) -> None:
        self.logger.clear_state()
