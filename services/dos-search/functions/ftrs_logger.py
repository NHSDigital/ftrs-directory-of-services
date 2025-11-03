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
        log_data: Optional[Dict[str, Any]] = None,
        **detail: object,
    ) -> None:
        extra = log_data
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
            extra = dict(log_data)
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
            (base_logger.info(message),)

    def info(
        self, message: str, log_data: Optional[Dict[str, Any]] = None, **detail: object
    ) -> None:
        self._log_with_level("info", message, log_data, **detail)

    def info_from_log_datax(self, message: str, log_data: Dict[str, Any]) -> None:
        """Convenience method with signature info(message, log_data)."""
        self.info(message, log_data)

    def warning(
        self, message: str, log_data: Optional[Dict[str, Any]] = None, **detail: object
    ) -> None:
        self._log_with_level("warning", message, log_data, **detail)

    def error(
        self, message: str, log_data: Optional[Dict[str, Any]] = None, **detail: object
    ) -> None:
        self._log_with_level("error", message, log_data, **detail)

    def exception(
        self, message: str, log_data: Optional[Dict[str, Any]] = None, **detail: object
    ) -> None:
        self._log_with_level("exception", message, log_data, **detail)

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
