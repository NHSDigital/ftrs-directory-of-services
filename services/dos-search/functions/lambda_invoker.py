from __future__ import annotations

import json
import os
from typing import Any

import boto3


def invoke_lambda_json(
    *,
    function_name: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Invoke another Lambda synchronously and return its decoded JSON payload.

    This is a small utility to support the "set of lambdas per endpoint" pattern.

    Notes:
    - Uses RequestResponse (sync) invocation.
    - Expects the target lambda to return a standard Lambda proxy response dict.
    """

    client = boto3.client("lambda")

    response = client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )

    raw_payload = response.get("Payload")
    if raw_payload is None:
        return {"statusCode": 502, "body": "Upstream lambda returned no payload"}

    decoded = raw_payload.read().decode("utf-8")
    if not decoded:
        return {"statusCode": 502, "body": "Upstream lambda returned empty payload"}

    return json.loads(decoded)


def get_orchestrator_mode() -> str:
    """Return orchestration mode for endpoint lambdas.

    Supported values:
    - "inline": do work in this lambda (default)
    - "lambda": delegate to a worker lambda (set-of-lambdas pattern)
    """

    return os.getenv("DOS_SEARCH_ORCHESTRATION_MODE", "inline").strip().lower()


def parse_lambda_name_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def get_worker_lambda_names() -> list[str]:
    """Return ordered list of worker lambda names for an endpoint.

    New config:
    - DOS_SEARCH_ORG_WORKER_LAMBDA_NAMES: comma-separated list

    Backwards compatible:
    - DOS_SEARCH_ORG_WORKER_LAMBDA_NAME: single name
    """

    names = parse_lambda_name_list(os.getenv("DOS_SEARCH_ORG_WORKER_LAMBDA_NAMES", ""))
    if names:
        return names

    single = os.getenv("DOS_SEARCH_ORG_WORKER_LAMBDA_NAME", "").strip()
    return [single] if single else []


def invoke_lambda_pipeline_json(
    *,
    function_names: list[str],
    initial_payload: dict[str, Any],
) -> dict[str, Any]:
    """Invoke multiple lambdas in order.

    The output of each invocation becomes the payload for the next invocation.
    """

    payload = initial_payload
    last_response: dict[str, Any] = {}

    for name in function_names:
        last_response = invoke_lambda_json(function_name=name, payload=payload)
        payload = last_response

    return last_response
