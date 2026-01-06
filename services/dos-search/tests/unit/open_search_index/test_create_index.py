from typing import Any
from unittest.mock import MagicMock, patch

import botocore.exceptions as _be
import pytest
import requests

from .loader import (
    make_add_auth,
    make_headers_response,
    make_resp,
)


def test_resolve_collection_endpoint_success(create_module: Any) -> None:
    cio = create_module
    fake_client = MagicMock()
    fake_client.list_collections.return_value = {
        "collectionSummaries": [{"id": "cid", "name": "mycol"}]
    }
    fake_client.batch_get_collection.return_value = {
        "collectionDetails": [{"collectionEndpoint": "https://endpoint.example"}]
    }
    with patch("create_open_search_index.boto3.client", return_value=fake_client):
        ep = cio.resolve_collection_endpoint("mycol", region="eu-west-1")
        assert ep == "https://endpoint.example"


def test_resolve_collection_endpoint_failure_returns_none(create_module: Any) -> None:
    cio = create_module

    def bad_client(*_args, **_kwargs):
        raise _be.BotoCoreError()

    with patch("create_open_search_index.boto3.client", bad_client):
        ep = cio.resolve_collection_endpoint("mycol", region=None)
        assert ep is None


def test_write_github_output_writes_file(
    tmp_path: Any, create_module: Any, monkeypatch: Any
) -> None:
    """Ensure write_github_output writes key=value lines to the path from GITHUB_OUTPUT without touching real env."""
    cio = create_module
    out = tmp_path / "ghout"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    cio.write_github_output({"endpoint": "https://x", "final_index": "idx"})
    data = out.read_text().splitlines()
    assert "endpoint=https://x" in data
    assert "final_index=idx" in data


def test_indexcreator_create_index_resolve_none(create_module: Any) -> None:
    cio = create_module
    creator = cio.IndexCreator("collection-name", "index", "", None)
    with patch(
        "create_open_search_index.resolve_collection_endpoint", return_value=None
    ):
        rc = creator.create_index()
        assert rc == 3


def test_indexcreator_create_index_head_delete_and_put(
    create_module: Any, tmp_path: Any
) -> None:
    cio = create_module
    creator = cio.IndexCreator("https://endpoint.example", "index", "", None)
    head = make_resp(200, "")
    delete = make_resp(204, "")
    put = make_resp(201, "")
    with (
        patch("create_open_search_index.sign_request_and_head", return_value=head),
        patch("create_open_search_index.sign_request_and_delete", return_value=delete),
        patch("create_open_search_index.sign_request_and_put", return_value=put),
    ):
        rc = creator.create_index()
        assert rc == 0


def test_indexcreator_create_index_head_404_put_failure(create_module: Any) -> None:
    cio = create_module
    creator = cio.IndexCreator("https://endpoint.example", "index", "", None)
    head = make_resp(404, "")
    put = make_resp(500, "Oops")
    with (
        patch("create_open_search_index.sign_request_and_head", return_value=head),
        patch("create_open_search_index.sign_request_and_put", return_value=put),
    ):
        rc = creator.create_index()
        assert rc == 4


def test_get_env_and_redact(create_module: Any, monkeypatch: Any) -> None:
    mod = create_module
    monkeypatch.delenv("NON_EXISTENT_ENV", raising=False)
    assert mod.get_env("NON_EXISTENT_ENV") is None
    assert mod.get_env("NON_EXISTENT_ENV", "def") == "def"
    assert mod.redact_auth_header({}) == ""


def test_get_collection_endpoint_by_id_empty_details(create_module: Any) -> None:
    mod = create_module

    class C:
        @staticmethod
        def list_collections():
            return {"collectionSummaries": []}

        @staticmethod
        def batch_get_collection(_ids=None, **_kwargs):
            return {"collectionDetails": []}

    assert mod.get_collection_endpoint_by_id(C(), "cid") is None


def test_resolve_collection_endpoint_boto_error(
    create_module: Any, monkeypatch: Any
) -> None:
    mod = create_module

    def fail_client(*_args, **_kwargs):
        raise _be.BotoCoreError()

    monkeypatch.setattr(mod.boto3, "client", fail_client)
    assert mod.resolve_collection_endpoint("name", None) is None


def test_send_prepared_request_raises(create_module: Any, monkeypatch: Any) -> None:
    mod = create_module
    aws_req = mod.build_aws_request(
        "GET", "https://example.com", "", mod.compute_payload_hash("")
    )

    def _send(*_args, **_kwargs):
        raise requests.RequestException("fail")

    monkeypatch.setattr(mod.requests.Session, "send", _send)
    with pytest.raises(requests.RequestException):
        mod.send_prepared_request(aws_req)


def test_sign_request_and_send_happy_path(
    create_module: Any, fake_credentials: Any, dummy_response: Any
) -> None:
    cio = create_module
    resp_obj = dummy_response(
        status_code=201,
        text='{"ok":true}',
        headers={"Content-Type": "application/json"},
        reason="Created",
    )
    with patch(
        "create_open_search_index.get_aws_signing_credentials",
        return_value=fake_credentials,
    ):
        mock_boto_client = MagicMock()
        mock_boto_client().get_caller_identity.return_value = {
            "Arn": "arn:aws:iam::123:role/fake"
        }
        with patch("create_open_search_index.boto3.client", mock_boto_client):
            with patch("create_open_search_index.SigV4Auth.add_auth", make_add_auth()):
                with (
                    patch(
                        "create_open_search_index.requests.Session.send",
                        return_value=resp_obj,
                    ) as mock_send,
                ):
                    result = cio.sign_request_and_send(
                        "PUT",
                        "https://example.com/index",
                        '{"a":1}',
                        region="eu-west-1",
                        service="aoss",
                    )
                    assert result is resp_obj
                    mock_send.assert_called_once()
                    sent = mock_send.call_args[0][0]
                    assert getattr(sent, "method", None) == "PUT"
                    assert getattr(sent, "url", "").endswith("/index")
                    headers = getattr(sent, "headers", {}) or {}
                    assert "Authorization" in headers
                    assert (
                        "x-amz-content-sha256" in {k.lower() for k in headers.keys()}
                        or "x-amz-content-sha256" in headers
                    )
                    body = getattr(sent, "body", getattr(sent, "data", None))
                    if isinstance(body, bytes):
                        body = body.decode("utf-8")
                    assert body == '{"a":1}'


def test_main_missing_inputs_returns_2(monkeypatch: Any, create_module: Any) -> None:
    cio = create_module
    monkeypatch.delenv("OPEN_SEARCH_DOMAIN", raising=False)
    monkeypatch.delenv("INDEX", raising=False)
    rc = cio.main([])
    assert rc == 2


def test_main_create_index_exception_returns_5(
    monkeypatch: Any, create_module: Any
) -> None:
    cio = create_module

    def fail_create(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(cio, "create_index", fail_create)
    rc = cio.main(["--open-search-domain", "https://example.com", "--index", "idx"])
    assert rc == 5


def test_log_response_headers_redaction_variants(
    create_module: Any, caplog: Any
) -> None:
    cio = create_module
    r = make_headers_response(
        {
            "Authorization": "AWS4-HMAC-SHA256 Credential=AKIA...,Signature=abc",
            "WWW-Authenticate": "x",
            "Set-Cookie": "a=1",
        }
    )
    caplog.set_level("INFO")
    cio.log_response_headers(r)
    assert any("Response headers" in r.message for r in caplog.records)


def test_build_index_name_and_endpoint_variants(create_module: Any) -> None:
    cio = create_module
    assert cio.build_index_name("index", "-ws") == "index-ws"
    assert cio.build_index_name("index", "ws") == "index-ws"
