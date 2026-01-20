import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from .helpers import (
    make_headers_response,
    make_text_response,
)


def test_prepare_payload_and_compute_hash_common(create_module: Any) -> None:
    cio = create_module
    payload = cio.prepare_payload()
    parsed = json.loads(payload)
    assert parsed == cio.MAPPINGS_PAYLOAD
    expected_empty = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert cio.compute_payload_hash("") == expected_empty


def test_redact_and_parse_response_variants_common(create_module: Any) -> None:
    cio = create_module
    raw = "AWS4-HMAC-SHA256 Credential=AKIA...,SignedHeaders=host;x-amz-date,Signature=abcdef"
    headers = {"Authorization": raw}
    redacted = cio.redact_auth_header(headers)
    assert "Signature=<redacted>" in redacted
    assert cio.parse_response_body(make_text_response("ok")) == "ok"
    assert cio.parse_response_body(make_text_response(raise_on_access=True)) == ""


def test_log_response_headers_unserializable_common(create_module: Any) -> None:
    cio = create_module
    r = make_headers_response({"bad": {1, 2}})
    cio.log_response_headers(r)


def test_get_aws_signing_credentials_missing_common(
    create_module: Any, monkeypatch: Any
) -> None:
    mod = create_module
    fake_session = MagicMock()
    fake_session.get_credentials.return_value = None
    monkeypatch.setattr("botocore.session.get_session", lambda: fake_session)
    with pytest.raises(RuntimeError):
        mod.get_aws_signing_credentials()
