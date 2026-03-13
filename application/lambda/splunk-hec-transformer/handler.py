import base64
import json
import os
import time
from datetime import datetime, timezone

DEFAULT_SPLUNK_INDEX = os.environ.get(
    "DEFAULT_SPLUNK_INDEX", "app_directoryofservices_dev"
)

_VALID_HEC_KEYS = {"event", "time", "source", "sourcetype", "index", "host", "fields"}
_POWERTOOLS_TS_FORMAT = "%Y-%m-%d %H:%M:%S,%f%z"


def _dropped(record: dict) -> dict:
    return {"recordId": record["recordId"], "result": "Dropped", "data": record["data"]}


def _ok(record: dict, data: str) -> dict:
    encoded = base64.b64encode(data.encode("utf-8")).decode("utf-8")
    return {"recordId": record["recordId"], "result": "Ok", "data": encoded}


def _is_hec_event(obj: dict) -> bool:
    """Return True if obj is already a valid Splunk HEC event envelope."""
    return "event" in obj and obj.keys() <= _VALID_HEC_KEYS


def _get_event_time(cwl_timestamp_ms: int, parsed: dict | None) -> float:
    """Resolve the best available timestamp for a log event.

    Prefers the CloudWatch logEvent millisecond timestamp, falls back to
    the Powertools 'timestamp' field, then to the current time.
    """
    if cwl_timestamp_ms:
        return cwl_timestamp_ms / 1000.0
    if isinstance(parsed, dict):
        try:
            dt = datetime.strptime(parsed.get("timestamp", ""), _POWERTOOLS_TS_FORMAT)
            return dt.astimezone(timezone.utc).timestamp()
        except (ValueError, TypeError):
            pass
    return time.time()


def _wrap_hec(message: str, cwl_timestamp_ms: int, log_group: str) -> str:
    """Wrap a log message in Splunk HEC event format if not already wrapped."""
    try:
        parsed = json.loads(message)
    except (json.JSONDecodeError, TypeError):
        parsed = None

    if isinstance(parsed, dict) and _is_hec_event(parsed):
        return message

    return json.dumps(
        {
            "time": _get_event_time(
                cwl_timestamp_ms, parsed if isinstance(parsed, dict) else None
            ),
            "source": log_group,
            "index": DEFAULT_SPLUNK_INDEX,
            "event": message,
        }
    )


def lambda_handler(event: dict, context: object) -> dict:
    """Firehose transformation Lambda for Splunk HEC Event delivery.

    Receives decompressed CloudWatch Logs envelopes from Kinesis Firehose.
    Extracts individual logEvents, wraps any that aren't already in HEC format,
    and concatenates them into a single output record per Firehose record.
    Non-DATA_MESSAGE and empty records are dropped.
    """
    output = []
    for record in event["records"]:
        raw = base64.b64decode(record["data"]).decode("utf-8").strip()

        try:
            envelope = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            output.append(_dropped(record))
            continue

        if (
            not isinstance(envelope, dict)
            or envelope.get("messageType") != "DATA_MESSAGE"
        ):
            output.append(_dropped(record))
            continue

        log_group = envelope.get("logGroup", "")
        hec_payload = "\n".join(
            _wrap_hec(le["message"].strip(), le.get("timestamp", 0), log_group)
            for le in envelope.get("logEvents", [])
            if le.get("message", "").strip()
        )

        output.append(_ok(record, hec_payload) if hec_payload else _dropped(record))

    return {"records": output}
