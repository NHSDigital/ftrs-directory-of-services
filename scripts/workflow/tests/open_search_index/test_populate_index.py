from typing import Any
from unittest.mock import MagicMock, patch

import botocore.exceptions as _be
import pytest

from .helpers import (
    make_add_auth,
    make_fake_bulk,
    make_paginator,
    make_raising_session,
    make_resp,
    make_session_with_resp,
)


def test_sign_request_and_send_sts_failure(
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
        # create a boto3.client stub whose get_caller_identity raises
        fake_sts = MagicMock()
        fake_sts.get_caller_identity.side_effect = _be.BotoCoreError()

        def fake_boto_client(service_name, *_args, **_kwargs):
            if service_name == "sts":
                return fake_sts
            raise RuntimeError

        with patch("create_open_search_index.boto3.client", fake_boto_client):
            with patch("create_open_search_index.SigV4Auth.add_auth", make_add_auth()):
                with patch(
                    "create_open_search_index.requests.Session.send",
                    return_value=resp_obj,
                ) as mock_send:
                    result = cio.sign_request_and_send(
                        "PUT",
                        "https://example.com/index",
                        '{"a":1}',
                        region="eu-west-1",
                        service="aoss",
                    )
                    assert result is resp_obj
                    assert mock_send.called


def test_find_collection_id_and_endpoint_variants(create_module: Any) -> None:
    mod = create_module

    class Client:
        @staticmethod
        def list_collections():
            return {"collectionSummaries": [{"id": "y", "name": "b"}]}

        @staticmethod
        def batch_get_collection(_ids=None, **_kwargs):
            _ = _kwargs
            return {"collectionDetails": [{"collectionEndpoint": "ep1"}]}

    cid = mod.find_collection_id_by_name(Client(), "b")
    assert cid == "y"
    ep = mod.get_collection_endpoint_by_id(Client(), "y")
    assert ep == "ep1"


def test_resolve_collection_endpoint_success_none(
    monkeypatch: Any, create_module: Any
) -> None:
    mod = create_module

    class FakeClient:
        @staticmethod
        def list_collections():
            return {"collectionSummaries": []}

    monkeypatch.setattr(mod.boto3, "client", lambda *_args, **_kwargs: FakeClient())
    assert mod.resolve_collection_endpoint("any", None) is None


def test_signed_request_session_adds_auth_and_sends(
    create_populate_module: Any,
) -> None:
    populate = create_populate_module
    fake_creds = MagicMock()
    with patch(
        "populate_open_search_index.get_aws_signing_credentials",
        return_value=fake_creds,
    ):
        with patch("populate_open_search_index.SigV4Auth.add_auth", make_add_auth()):
            session = populate.SignedRequestsSession(None)
            sent = MagicMock()
            sent.return_value = make_resp(200, text="", json_value={})
            session.session.send = sent
            resp = session.request("PUT", "https://example/index", '{"a":1}')
            assert resp.status_code == 200
            assert sent.called
            prepared = sent.call_args[0][0]
            assert "Authorization" in getattr(prepared, "headers", {})


def test_index_bulk_success_parsing(create_populate_module: Any) -> None:
    populate = create_populate_module
    session = MagicMock()
    session.request.return_value = make_resp(
        200,
        json_value={"items": [{"index": {"status": 201}}, {"index": {"status": 201}}]},
    )
    ok, total = populate.index_bulk(
        session, "https://example", "idx", [{"primary_key": "a"}, {"primary_key": "b"}]
    )
    assert ok == 2
    assert total == 2


def test_index_records_bulk_failure(create_populate_module: Any) -> None:
    populate = create_populate_module
    records = [{"primary_key": f"id{i}", "x": i} for i in range(4)]
    fake_bulk = make_fake_bulk(delta=1)
    with patch.object(populate, "index_bulk", fake_bulk):
        session = MagicMock()
        success, total = populate.index_records(
            session, "https://example", "idx", records, batch_size=2
        )
        assert total == 4
        assert success == 2


def test_index_bulk_non_200_and_json_error(create_populate_module: Any) -> None:
    mod = create_populate_module
    resp = make_resp(200, text="ok", raise_json=True)
    success, total = mod.index_bulk(
        make_session_with_resp(resp), "https://ep", "idx", [{"primary_key": "a"}]
    )
    assert success == 0
    assert total == 1
    success2, total2 = mod.index_bulk(
        make_session_with_resp(resp), "https://ep", "idx", [{"primary_key": "a"}]
    )
    assert success2 == 0
    assert total2 == 1


def test_index_records_bulk_path_and_chunking(create_populate_module: Any) -> None:
    mod = create_populate_module
    resp = make_resp(
        200,
        text="ok",
        json_value={"items": [{"index": {"status": 201}}, {"index": {"status": 201}}]},
    )
    records = [{"primary_key": "1"}, {"primary_key": "2"}, {"primary_key": "3"}]
    _, total = mod.index_records(
        make_session_with_resp(resp), "https://ep", "idx", records, batch_size=2
    )
    assert total == 3


def test_index_single_record_transient_failure(create_populate_module: Any) -> None:
    mod = create_populate_module
    session = MagicMock()
    session.request.return_value = make_resp(500, "server error")
    ok, status, _ = mod.index_single_record(
        session, "https://ep", "idx", {"primary_key": "p1"}
    )
    assert ok is False
    assert status == 500


def test_scan_dynamodb_table_no_projection(create_populate_module: Any) -> None:
    mod = create_populate_module
    client = make_paginator([{"Items": []}])
    items = mod.scan_dynamodb_table(client, "tbl", [])
    assert items == []


def test_index_bulk_partial_error_counts(create_populate_module: Any) -> None:
    mod = create_populate_module
    resp = make_resp(
        200,
        json_value={
            "items": [
                {"index": {"status": 201}},
                {"index": {"status": 500}},
                {"index": {}},
            ]
        },
    )
    records = [
        {"primary_key": "p1", "a": 1},
        {"primary_key": "p2", "b": 2},
        {"primary_key": "p3", "c": 3},
    ]
    ok, total = mod.index_bulk(
        make_session_with_resp(resp), "https://ep", "idx", records
    )
    assert ok == 1
    assert total == 3


def test_signed_requests_session_add_auth_raises(
    monkeypatch: Any, create_populate_module: Any
) -> None:
    mod = create_populate_module

    def bad_add(_self, _aws_req):
        raise RuntimeError

    monkeypatch.setattr(
        mod,
        "SigV4Auth",
        type(
            "X",
            (),
            {"__init__": lambda self, *_args, **_kwargs: None, "add_auth": bad_add},
        ),
    )
    monkeypatch.setattr(mod, "get_aws_signing_credentials", lambda: "creds")
    session = mod.SignedRequestsSession(None)
    with pytest.raises(RuntimeError):
        session.request("PUT", "https://example/index", "{}")


def test_index_records_skips_missing_docid_field(create_populate_module: Any) -> None:
    mod = create_populate_module
    records = [{"x": 1}, {"y": 2}]
    session = MagicMock()
    success, total = mod.index_records(
        session, "https://ep", "idx", records, batch_size=1
    )
    assert success == 0
    assert total == len(records)


def test_index_bulk_items_with_missing_index_key(create_populate_module: Any) -> None:
    mod = create_populate_module
    resp = make_resp(
        200, json_value={"items": [{"not_index": {}}, {"index": {"status": 201}}]}
    )
    ok, total = mod.index_bulk(
        make_session_with_resp(resp),
        "https://ep",
        "idx",
        [{"primary_key": "p1", "a": 1}, {"primary_key": "p2", "b": 2}],
    )
    assert ok == 1
    assert total == 2


def test_index_bulk_invalid_json_and_non_200(create_populate_module: Any) -> None:
    mod = create_populate_module
    resp = make_resp(500, json_value={"items": []})
    ok, total = mod.index_bulk(
        make_session_with_resp(resp),
        "https://ep",
        "idx",
        [{"primary_key": "p1", "a": 1}],
    )
    assert ok == 0
    assert total == 1


def test_index_bulk_mixed_items(create_populate_module: Any) -> None:
    mod = create_populate_module
    resp = make_resp(
        200,
        json_value={
            "items": [
                {"index": {"status": 201}},
                {"index": {"status": 500}},
                {"not_index": {}},
            ]
        },
    )
    ok, total = mod.index_bulk(
        make_session_with_resp(resp),
        "https://ep",
        "idx",
        [{"primary_key": "a"}, {"primary_key": "b"}, {"primary_key": "c"}],
    )
    assert ok == 1
    assert total == 3


def test_index_bulk_json_raises_treated_as_failures(
    create_populate_module: Any,
) -> None:
    mod = create_populate_module
    resp = make_resp(200, raise_json=True)
    ok, total = mod.index_bulk(
        make_session_with_resp(resp),
        "https://ep",
        "idx",
        [{"primary_key": "a"}, {"primary_key": "b"}],
    )
    assert ok == 0
    assert total == 2


def test_index_single_record_unexpected_exception(create_populate_module: Any) -> None:
    mod = create_populate_module
    ok, status, body = mod.index_single_record(
        make_raising_session(RuntimeError("boom")),
        "https://ep",
        "idx",
        {"primary_key": "p1"},
    )
    assert ok is False
    assert status == 500
    assert "boom" in body


def test_index_records_chunk_partial_failure_logs(
    create_populate_module: Any, caplog: Any
) -> None:
    mod = create_populate_module
    records = [
        {"primary_key": "1"},
        {"primary_key": "2"},
        {"primary_key": "3"},
        {"primary_key": "4"},
    ]
    # make index_bulk report fewer successes than attempted to trigger the log.error
    with patch.object(mod, "index_bulk", make_fake_bulk(delta=100)):
        caplog.set_level("ERROR")
        success, total = mod.index_records(
            MagicMock(), "https://ep", "idx", records, batch_size=2
        )
    assert total == 4
    assert success == 0
    assert any("Bulk chunk had" in r.message for r in caplog.records)


def test_main_passes_projection_to_scan(create_populate_module: Any) -> None:
    mod = create_populate_module
    called = {}

    def fake_scan(_client, table, attrs):
        called["table"] = table
        called["attrs"] = attrs
        return []

    with (
        patch(
            "populate_open_search_index.prepare_dynamodb_client",
            return_value=MagicMock(),
        ),
        patch("populate_open_search_index.scan_dynamodb_table", side_effect=fake_scan),
        patch(
            "populate_open_search_index.SignedRequestsSession", return_value=MagicMock()
        ),
    ):
        rc = mod.main(["--endpoint", "https://example", "--final-index", "triage_code"])
        assert rc == 0

    assert "attrs" in called
    assert "id" in called["attrs"]
    assert "symptomGroupSymptomDiscriminators" in called["attrs"]


def test_transform_full_item_maps_id_and_nested(create_populate_module: Any) -> None:
    mod = create_populate_module
    sample = {
        "id": "6f3d7dd4-e50b-5d8d-be2b-455f091b4df2",
        "field": "document",
        "active": True,
        "symptomGroupSymptomDiscriminators": [
            {"sd": 4052, "sg": 1006},
            {"sd": 4052, "sg": 1004},
        ],
    }

    out = mod.transform_records([sample])
    assert isinstance(out, list)
    assert len(out) == 1
    doc = out[0]
    assert "primary_key" in doc
    assert doc["primary_key"] == "6f3d7dd4-e50b-5d8d-be2b-455f091b4df2"
    nested = doc.get(mod.NESTED_COLLECTION_FIELD)
    assert isinstance(nested, list)
    assert len(nested) == 2
    assert nested[0]["sg"] == 1006
    assert nested[0]["sd"] == 4052
