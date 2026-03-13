import base64
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import handler as h  # noqa: E402


def _encode(obj: dict) -> str:
    return base64.b64encode(json.dumps(obj).encode()).decode()


def _decode(record: dict) -> str:
    return base64.b64decode(record["data"]).decode()


def _cwl_envelope(log_events: list[dict], log_group: str = "/aws/lambda/test") -> dict:
    return {
        "messageType": "DATA_MESSAGE",
        "logGroup": log_group,
        "logStream": "stream",
        "logEvents": log_events,
    }


def _firehose_event(envelopes: list[dict]) -> dict:
    return {
        "records": [
            {"recordId": str(i), "data": _encode(env)}
            for i, env in enumerate(envelopes)
        ]
    }


def _invoke(envelopes: list[dict]) -> list[dict]:
    return h.lambda_handler(_firehose_event(envelopes), None)["records"]


class TestIsHecEvent:
    def test_minimal_valid(self) -> None:
        assert h._is_hec_event({"event": "hello"}) is True

    def test_all_valid_keys(self) -> None:
        assert (
            h._is_hec_event(
                {"event": "x", "time": 1.0, "source": "s", "index": "i", "host": "h"}
            )
            is True
        )

    def test_missing_event_key(self) -> None:
        assert h._is_hec_event({"time": 1.0, "source": "s"}) is False

    def test_unknown_key(self) -> None:
        assert h._is_hec_event({"event": "x", "unknown_key": "y"}) is False

    def test_empty(self) -> None:
        assert h._is_hec_event({}) is False


class TestGetEventTime:
    def test_cwl_timestamp_wins(self) -> None:
        result = h._get_event_time(
            1_700_000_000_000, {"timestamp": "2023-01-01 00:00:00,000+0000"}
        )
        assert result == pytest.approx(1_700_000_000.0)

    def test_falls_back_to_powertools_timestamp(self) -> None:
        result = h._get_event_time(0, {"timestamp": "2024-03-01 12:00:00,000+0000"})
        expected = datetime(2024, 3, 1, 12, 0, 0, tzinfo=timezone.utc).timestamp()
        assert result == pytest.approx(expected)

    def test_falls_back_to_now_when_no_cwl_ts(self) -> None:
        before = time.time()
        result = h._get_event_time(0, None)
        assert before <= result <= time.time()

    def test_falls_back_to_now_on_bad_powertools_ts(self) -> None:
        before = time.time()
        result = h._get_event_time(0, {"timestamp": "not-a-date"})
        assert before <= result <= time.time()


class TestWrapHec:
    def test_already_hec_passes_through_unchanged(self) -> None:
        msg = json.dumps({"event": "something", "time": 1.0, "source": "s"})
        assert h._wrap_hec(msg, 1_000_000, "/aws/lambda/test") == msg

    def test_plain_string_is_wrapped(self) -> None:
        result = json.loads(h._wrap_hec("plain log", 1_700_000_000_000, "/lg"))
        assert result["event"] == "plain log"
        assert result["source"] == "/lg"
        assert result["time"] == pytest.approx(1_700_000_000.0)
        assert "index" in result

    def test_non_hec_json_is_wrapped(self) -> None:
        msg = json.dumps({"level": "INFO", "message": "booted"})
        result = json.loads(h._wrap_hec(msg, 1_700_000_000_000, "/lg"))
        assert result["event"] == msg

    def test_uses_default_index(self) -> None:
        result = json.loads(h._wrap_hec("log", 1_000, "/lg"))
        assert result["index"] == h.DEFAULT_SPLUNK_INDEX

    def test_cwl_timestamp_takes_priority_over_powertools(self) -> None:
        msg = json.dumps({"timestamp": "2020-01-01 00:00:00,000+0000", "message": "x"})
        result = json.loads(h._wrap_hec(msg, 1_700_000_000_000, "/lg"))
        assert result["time"] == pytest.approx(1_700_000_000.0)


class TestLambdaHandler:
    def test_raw_log_is_wrapped_to_hec(self) -> None:
        envelope = _cwl_envelope(
            [{"message": "hello world", "timestamp": 1_700_000_000_000}]
        )
        records = _invoke([envelope])
        assert records[0]["result"] == "Ok"
        payload = json.loads(_decode(records[0]))
        assert payload["event"] == "hello world"
        assert payload["source"] == "/aws/lambda/test"

    def test_already_hec_passes_through(self) -> None:
        hec_msg = json.dumps({"event": "pre-formatted", "time": 1.0, "source": "s"})
        envelope = _cwl_envelope([{"message": hec_msg, "timestamp": 1_700_000_000_000}])
        records = _invoke([envelope])
        assert records[0]["result"] == "Ok"
        assert _decode(records[0]) == hec_msg

    def test_multiple_events_are_newline_delimited(self) -> None:
        envelope = _cwl_envelope(
            [
                {"message": "line one", "timestamp": 1_000_000},
                {"message": "line two", "timestamp": 2_000_000},
            ]
        )
        records = _invoke([envelope])
        lines = _decode(records[0]).split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["event"] == "line one"
        assert json.loads(lines[1])["event"] == "line two"

    def test_record_id_is_preserved(self) -> None:
        envelope = _cwl_envelope([{"message": "x", "timestamp": 1_000}])
        result = h.lambda_handler(
            {"records": [{"recordId": "abc-123", "data": _encode(envelope)}]}, None
        )
        assert result["records"][0]["recordId"] == "abc-123"

    def test_multiple_firehose_records(self) -> None:
        envelopes = [
            _cwl_envelope([{"message": "rec-0", "timestamp": 1_000}]),
            _cwl_envelope([{"message": "rec-1", "timestamp": 2_000}]),
        ]
        records = _invoke(envelopes)
        assert len(records) == 2
        assert all(r["result"] == "Ok" for r in records)

    def test_invalid_json_dropped(self) -> None:
        bad_data = base64.b64encode(b"not json at all").decode()
        result = h.lambda_handler(
            {"records": [{"recordId": "r1", "data": bad_data}]}, None
        )
        assert result["records"][0]["result"] == "Dropped"

    def test_control_message_dropped(self) -> None:
        envelope = {
            "messageType": "CONTROL_MESSAGE",
            "logGroup": "/aws/lambda/test",
            "logEvents": [],
        }
        assert _invoke([envelope])[0]["result"] == "Dropped"

    def test_empty_log_events_dropped(self) -> None:
        assert _invoke([_cwl_envelope([])])[0]["result"] == "Dropped"

    def test_whitespace_only_message_dropped(self) -> None:
        assert (
            _invoke([_cwl_envelope([{"message": "   ", "timestamp": 1_000}])])[0][
                "result"
            ]
            == "Dropped"
        )

    def test_non_dict_json_dropped(self) -> None:
        bad_data = base64.b64encode(json.dumps([1, 2, 3]).encode()).decode()
        result = h.lambda_handler(
            {"records": [{"recordId": "r1", "data": bad_data}]}, None
        )
        assert result["records"][0]["result"] == "Dropped"

    def test_custom_index_from_env(self) -> None:
        envelope = _cwl_envelope([{"message": "log", "timestamp": 1_000}])
        with patch.object(h, "DEFAULT_SPLUNK_INDEX", "my_custom_index"):
            records = _invoke([envelope])
        assert json.loads(_decode(records[0]))["index"] == "my_custom_index"
