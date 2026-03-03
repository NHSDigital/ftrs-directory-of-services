import os
import time
from typing import Any, Optional

from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import fetch_or_set_correlation_id
from ftrs_common.utils.request_id import fetch_or_set_request_id

from functions.logbase import DosSearchLogBase

PLACEHOLDER = "Value not found. Please check if this value was provided in the request."

_CORRELATION_ID_INDEX = 1
_MESSAGE_ID_INDEX = 2


def setup_request(event: dict[str, Any], logger: Logger) -> None:
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}

    log_data = _extract_mandatory(headers)
    fetch_or_set_request_id(header_id=_get_header(headers, "nhsd-request-id"))
    fetch_or_set_correlation_id(existing=_get_header(headers, "nhsd-correlation-id"))

    logger.append_keys(**log_data)

    details = _extract_one_time(event, headers)
    logger.log(
        DosSearchLogBase.DOS_SEARCH_001, **details, dos_message_category="REQUEST"
    )


def get_response_size_and_duration(
    fhir_resource: Optional[FHIRResourceModel], start: float, logger: Logger
) -> tuple[int, int]:
    duration_ms = int((time.time() - start) * 1000)
    try:
        body = fhir_resource.model_dump_json()
        response_size = len(body.encode("utf-8"))
    except Exception:
        response_size = 0
        logger.log(
            DosSearchLogBase.DOS_SEARCH_010,
            dos_response_time=f"{duration_ms}ms",
            dos_response_size=response_size,
        )
    return response_size, duration_ms


def _get_header(headers: dict[str, Any], *names: str) -> Optional[str]:
    for n in names:
        val = headers.get(n)
        if val not in (None, ""):
            return val
    return None


def _extract_mandatory(headers: dict[str, Any]) -> dict[str, Any]:
    corr_header = _get_header(headers, "nhsd-correlation-id")
    split_corr_header = corr_header.split(".") if corr_header else []

    return {
        "dos_nhsd_correlation_id": (
            next(
                iter(
                    split_corr_header[_CORRELATION_ID_INDEX : _CORRELATION_ID_INDEX + 1]
                ),
                None,
            )
            or PLACEHOLDER
        ),
        "dos_message_id": (
            next(
                iter(split_corr_header[_MESSAGE_ID_INDEX : _MESSAGE_ID_INDEX + 1]), None
            )
            or PLACEHOLDER
        ),
        "dos_nhsd_request_id": (_get_header(headers, "nhsd-request-id") or PLACEHOLDER),
        "dos_message_category": "LOGGING",
    }


def _extract_one_time(event: dict[str, Any], headers: dict[str, Any]) -> dict[str, Any]:
    details: dict[str, Any] = {}

    details["dos_search_api_version"] = _get_header(headers, "version") or PLACEHOLDER
    details["connecting_party_end_user_role"] = (
        _get_header(headers, "end-user-role") or PLACEHOLDER
    )
    details["connecting_party_application_id"] = (
        _get_header(headers, "application-id") or PLACEHOLDER
    )
    details["connecting_party_application_name"] = (
        _get_header(headers, "application-name") or PLACEHOLDER
    )

    request_context = dict(event.get("requestContext") or {})
    request_context.pop("identity", None)
    request_context.pop("accountId", None)

    details["request_params"] = {
        "query_params": event.get("queryStringParameters") or {},
        "path_params": event.get("pathParameters") or {},
        "request_context": request_context,
    }

    details["dos_environment"] = os.environ.get("ENVIRONMENT") or PLACEHOLDER
    details["lambda_version"] = (
        os.environ.get("AWS_LAMBDA_FUNCTION_VERSION") or PLACEHOLDER
    )

    return details
