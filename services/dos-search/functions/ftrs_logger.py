import inspect
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

from aws_lambda_powertools.logging import Logger as PowertoolsLogger


class FtrsLogger:
    """Service-local wrapper that adds FTRS structured fields to powertools logs.

    Usage:
        f = FtrsLogger(service='dos-search')
        f.info('message', event=my_event)

    Behavior:
    - Builds an `extra` dict with mandatory ftrs_ and nhsd_ fields and optional Opt_ fields
    - Calls powertools Logger with `extra=...` so powertools merges it into its JSON output
    - Optionally prints a debug preview when debug=True
    - Placeholder for missing values is configurable via ENV `FTRS_LOG_PLACEHOLDER` (default 'TBC').
        If set to 'NULL' the wrapper will emit Python None (JSON null) for missing values.
    """

    def __init__(self, service: str = "ftrs", debug: bool = False) -> None:
        self._logger = PowertoolsLogger(service=service)
        self._service = service
        self.debug = debug
        # remember last appended correlation id so we can expose it later
        self._last_appended_correlation: Optional[str] = None
        # placeholder behaviour
        self._placeholder_raw = os.environ.get("FTRS_LOG_PLACEHOLDER", "TBC")

    # --- helper utilities -------------------------------------------------
    def _placeholder(self) -> Optional[str]:
        """Return configured placeholder or None if configured as NULL."""
        if self._placeholder_raw and self._placeholder_raw.upper() == "NULL":
            return None
        return self._placeholder_raw

    @staticmethod
    def _normalize_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
        """Return a case-insensitive mapping for header lookup (lowercased keys)."""
        if not headers or not isinstance(headers, dict):
            return {}
        return {k.lower(): v for k, v in headers.items()}

    @staticmethod
    def _first_of(mapping: Dict[str, Any], keys: Iterable[str]) -> Optional[str]:
        """Return the first non-empty mapping value for keys (case-sensitive keys assumed already normalized as needed)."""
        for k in keys:
            v = mapping.get(k)
            if v not in (None, ""):
                return v
        return None

    # --- extraction -------------------------------------------------------
    def _extract(self, event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract APIM headers and common event fields into the structured 'extra' dict.

        All mandatory fields are present; missing values use the configured placeholder.
        Optional one-time fields are prefixed with 'Opt_'.
        """
        placeholder = self._placeholder()

        headers = (
            {}
            if not event or not isinstance(event, dict)
            else (event.get("headers") or {})
        )
        hdr_lower = self._normalize_headers(headers)

        def h(*names: str) -> Optional[str]:
            # try original casing keys first, then lowercased mapping
            for n in names:
                if n in headers and headers.get(n) not in (None, ""):
                    return headers.get(n)
            # fallback to lowercased lookup of provided names
            for n in names:
                val = hdr_lower.get(n.lower())
                if val not in (None, ""):
                    return val
            return None

        out: Dict[str, Any] = {}

        # NHSD correlation id
        corr = h("NHSD-Correlation-ID", "X-Request-Id") or placeholder
        out["ftrs_nhsd_correlation_id"] = corr
        out["nhsd_correlation_id"] = corr

        # NHSD request id
        reqid = h("NHSD-Request-ID") or placeholder
        out["ftrs_nhsd_request_id"] = reqid
        out["nhsd_request_id"] = reqid

        # APIM message id
        msgid = (
            h("x-apim-msg-id", "X-Message-Id", "apim-message-id", "ftrs-message-id")
            or placeholder
        )
        out["ftrs_message_id"] = msgid
        out["nhsd_message_id"] = msgid

        # Mandatory/default ftrs fields
        out["ftrs_message_category"] = "LOGGING"
        out["ftrs_environment"] = (
            os.environ.get("ENVIRONMENT")
            or os.environ.get("WORKSPACE")
            or self._service
            or placeholder
        )
        out["ftrs_api_version"] = h("x-api-version", "api-version") or placeholder
        out["ftrs_lambda_version"] = (
            os.environ.get("AWS_LAMBDA_FUNCTION_VERSION") or placeholder
        )
        out["ftrs_response_time"] = placeholder
        out["ftrs_response_size"] = placeholder

        # Optional one-time fields prefixed with 'Opt_'
        end_user_role = (
            h("x-end-user-role")
            or (event.get("end_user_role") if isinstance(event, dict) else None)
            or (
                event.get("requestContext", {})
                .get("authorizer", {})
                .get("end_user_role")
                if isinstance(event, dict)
                else None
            )
            or placeholder
        )
        out["Opt_ftrs_end_user_role"] = end_user_role

        client_id = (
            h("x-client-id")
            or (event.get("client_id") if isinstance(event, dict) else None)
            or placeholder
        )
        out["Opt_ftrs_client_id"] = client_id

        app_name = (
            h("x-application-name")
            or (event.get("application_name") if isinstance(event, dict) else None)
            or placeholder
        )
        out["Opt_ftrs_application_name"] = app_name

        # Request params (queryStringParameters + pathParameters)
        req_params: Dict[str, Any] = {}
        if isinstance(event, dict):
            qs = event.get("queryStringParameters") or {}
            path_params = event.get("pathParameters") or {}
            if isinstance(qs, dict):
                req_params.update(qs)
            if isinstance(path_params, dict):
                req_params.update(path_params)
        out["Opt_ftrs_request_parms"] = req_params or {}

        return out

    # --- powertools context -----------------------------------------------
    def _append_powertools_context(self, extra: Dict[str, Any]) -> None:
        """Append keys to powertools logger context where possible.

        Best-effort: if powertools Logger implements append_keys we call it; otherwise ignore.
        """
        try:
            corr = extra.get("ftrs_nhsd_correlation_id")
            if corr and corr != self._placeholder():
                append = getattr(self._logger, "append_keys", None)
                if callable(append):
                    try:
                        append(correlation_id=corr)
                        self._last_appended_correlation = corr
                    except Exception:
                        self._last_appended_correlation = corr
                else:
                    # still remember the value locally
                    self._last_appended_correlation = corr
        except Exception:
            # swallow; best-effort only
            pass

    # --- debug preview ---------------------------------------------------
    def _debug_preview(self, message: str, extra: Dict[str, Any]) -> None:
        if not self.debug:
            return
        try:
            # use standard logger for debug preview to respect handlers
            log = logging.getLogger(self._service + "-preview")
            if not log.handlers:
                ch = logging.StreamHandler()
                ch.setFormatter(logging.Formatter("%(message)s"))
                log.addHandler(ch)
            log.info(json.dumps({"message": message, **extra}, indent=2))
        except Exception:
            print(message, extra)

    # --- public helpers --------------------------------------------------
    def get_powertools_metadata(
        self, context: Optional[object] = None
    ) -> Dict[str, Any]:
        """Return a best-effort view of fields powertools would include at top level.

        Useful for tests or responses; not authoritative (CloudWatch is).
        """
        placeholder = self._placeholder()
        meta: Dict[str, Any] = {}

        now = datetime.now(timezone.utc)
        ms = int(now.microsecond / 1000)
        meta["timestamp"] = (
            now.strftime("%Y-%m-%d %H:%M:%S") + f",{ms:03d}" + now.strftime("%z")
        )

        location = "<unknown>"
        try:
            stack = inspect.stack()
            for frame_info in stack[1:]:
                if frame_info.filename != __file__:
                    location = f"{frame_info.function}:{frame_info.lineno}"
                    break
        except Exception:
            location = "<unknown>"
        meta["location"] = location

        meta["function_name"] = (
            os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or self._service
        )
        meta["function_memory_size"] = (
            os.environ.get("AWS_LAMBDA_FUNCTION_MEMORY_SIZE") or placeholder
        )
        meta["function_arn"] = os.environ.get("AWS_LAMBDA_FUNCTION_ARN") or placeholder

        function_request_id = placeholder
        try:
            if context is not None and hasattr(context, "aws_request_id"):
                function_request_id = getattr(context, "aws_request_id")
        except Exception:
            function_request_id = placeholder
        meta["function_request_id"] = function_request_id

        meta["correlation_id"] = self._last_appended_correlation or placeholder
        meta["xray_trace_id"] = (
            os.environ.get("_X_AMZN_TRACE_ID")
            or os.environ.get("AWS_XRAY_TRACE_ID")
            or placeholder
        )
        meta["level"] = "TBC"
        return meta

    def _log_with_level(
        self,
        level: str,
        message: str,
        event: Optional[Dict[str, Any]] = None,
        **detail: object,
    ) -> None:
        extra = self._extract(event)

        # convert detail (kwargs) to dict for manipulation
        detail_map = dict(detail) if detail else {}

        # Allow certain ftrs_* fields to be provided as top-level overrides
        override_keys = {
            "ftrs_response_time",
            "ftrs_response_size",
            "ftrs_message_category",
            "ftrs_response",
        }
        if detail_map:
            extra = dict(extra)
            for k in list(detail_map.keys()):
                if k in override_keys:
                    extra[k] = detail_map.pop(k)
            if detail_map:
                extra["detail"] = detail_map

        # append powertools context where possible
        self._append_powertools_context(extra)

        # debug preview
        self._debug_preview(message, extra)

        # call powertools
        try:
            if level == "info":
                self._logger.info(message, extra=extra)
            elif level == "warning":
                self._logger.warning(message, extra=extra)
            elif level == "error":
                self._logger.error(message, extra=extra)
            elif level == "exception":
                self._logger.exception(message, extra=extra)
            else:
                self._logger.info(message, extra=extra)
        except TypeError:
            base_logger = logging.getLogger(self._service)
            base_logger.info(message)

    def info(
        self, message: str, event: Optional[Dict[str, Any]] = None, **detail: object
    ) -> None:
        self._log_with_level("info", message, event, **detail)

    def info_from_event(self, message: str, event: Dict[str, Any]) -> None:
        """Convenience method with signature info(message, event)."""
        self.info(message, event)

    def warning(
        self, message: str, event: Optional[Dict[str, Any]] = None, **detail: object
    ) -> None:
        self._log_with_level("warning", message, event, **detail)

    def error(
        self, message: str, event: Optional[Dict[str, Any]] = None, **detail: object
    ) -> None:
        self._log_with_level("error", message, event, **detail)

    def exception(
        self, message: str, event: Optional[Dict[str, Any]] = None, **detail: object
    ) -> None:
        self._log_with_level("exception", message, event, **detail)

    def log_payload_only(
        self,
        message: Optional[str] = None,
        event: Optional[Dict[str, Any]] = None,
        level: int = logging.INFO,
        **detail: object,
    ) -> None:
        """Emit only the structured payload (no powertools metadata).

        The payload is JSON containing the extracted ftrs_* / nhsd_* / Opt_* fields plus
        an optional message and any detail keys. This is useful when you want to
        write searchable JSON fields without the powertools metadata wrapper.
        """
        payload = self._extract(event)
        if detail:
            payload = dict(payload)
            payload.update(dict(detail))
        if message is not None:
            payload = dict(payload)
            payload["message"] = message

        try:
            base_logger = logging.getLogger(self._service)
            if not base_logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter("%(message)s"))
                base_logger.addHandler(handler)
            base_logger.log(level, json.dumps(payload))
        except Exception:
            print(json.dumps(payload))

    def info_payload(
        self, message: str, event: Optional[Dict[str, Any]] = None, **detail: object
    ) -> None:
        self.log_payload_only(
            message=message, event=event, level=logging.INFO, **detail
        )


# end of ftrs_logger.py
