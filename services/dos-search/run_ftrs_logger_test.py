#!/usr/bin/env python3
import json
import logging
import os
import sys
from pathlib import Path

# Ensure env used by logger is available
os.environ.setdefault("ENVIRONMENT", "Development")
os.environ.setdefault("AWS_LAMBDA_FUNCTION_VERSION", "1")

from functions.ftrs_logger import FtrsLogger

OUT_DIR = Path(__file__).resolve().parent


def configure_root_stdout() -> None:
    root = logging.getLogger()
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(handler)
    root.setLevel(logging.INFO)


def main() -> None:
    configure_root_stdout()

    logger = FtrsLogger(service="dos-search", debug=True)

    event = {
        "headers": {
            "NHSD-Correlation-ID": "<EXAMPLE_CORRELATION_ID>",
            "NHSD-Request-ID": "<EXAMPLE_REQUEST_ID>",
            "x-apim-msg-id": "<EXAMPLE_APIM_MESSAGE_ID>",
            "x-end-user-role": "clinician",
            "x-client-id": "<EXAMPLE_CLIENT_ID>",
            "x-application-name": "example-app",
            "x-api-version": "v1.0.0",
        },
        "queryStringParameters": {"odsCode": "A12345"},
        "pathParameters": {"path": "p"},
    }

    print("\n=== RUN FTRS LOGGER TEST (refactored) ===")

    extracted = logger._extract(event)
    print("\n--- extracted extra ---")
    print(json.dumps(extracted, indent=2))

    # best-effort powertools-like meta
    from types import SimpleNamespace

    ctx = SimpleNamespace(aws_request_id="local-req-1")
    meta = logger.get_powertools_metadata(context=ctx)
    print("\n--- powertools-like meta (best-effort) ---")
    print(json.dumps(meta, indent=2))

    merged = {**meta, **extracted}
    print("\n--- merged meta + extra ---")
    print(json.dumps(merged, indent=2))

    # persist outputs for inspection
    (OUT_DIR / "ftrs_logger_test_output.json").write_text(
        json.dumps({"meta": meta, "extra": extracted, "merged": merged}, indent=2)
    )

    # ensure powertools logger prints to stdout (Powertools attaches its own handler/formatter)
    try:
        # use the service logger name
        plog = logging.getLogger("dos-search")
        if not any(isinstance(h, logging.StreamHandler) for h in plog.handlers):
            plog.addHandler(logging.StreamHandler(sys.stdout))
    except Exception:
        pass

    print("\n--- emitting powertools log via FtrsLogger.info() ---")
    logger.info(
        "Test log via powertools (refactored)",
        event=event,
        ods_code="A12345",
        ftrs_response_time="42ms",
        ftrs_response_size=1234,
    )

    print("\n--- emitting payload-only ---")
    logger.info_payload("Payload-only (refactored)", event=event, ods_code="A12345")

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
