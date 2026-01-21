from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch


def test_populate_indexes_records_from_dynamodb_scan_no_aws(
    create_populate_module: Any,
) -> None:
    mod = create_populate_module

    raw_items = [
        {
            "id": {"S": "abc"},
            "symptomGroupSymptomDiscriminators": {
                "L": [
                    {"M": {"sg": {"N": "1006"}, "sd": {"N": "4052"}}},
                    {"M": {"sg": {"N": "1004"}, "sd": {"N": "4052"}}},
                ]
            },
        }
    ]

    deserialized = mod.deserialize_dynamodb_items(raw_items)
    assert deserialized == [
        {
            "id": "abc",
            "symptomGroupSymptomDiscriminators": [
                {"sg": 1006, "sd": 4052},
                {"sg": 1004, "sd": 4052},
            ],
        }
    ]

    docs = mod.transform_records(deserialized, mod.DEFAULT_SCHEMA_CONFIG)
    assert len(docs) == 1
    doc = docs[0]
    assert doc["primary_key"] == "abc"
    assert isinstance(doc.get(mod.NESTED_COLLECTION_FIELD), list)
    assert len(doc[mod.NESTED_COLLECTION_FIELD]) == 2

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "items": [
            {"index": {"status": 201}},
        ]
    }

    fake_session = MagicMock()
    fake_session.request.return_value = fake_response

    success, total = mod.index_records(
        fake_session,
        endpoint="https://example",
        index_name="idx",
        records=docs,
        batch_size=25,
    )

    assert total == 1
    assert success == 1

    called_url = fake_session.request.call_args[0][1]
    assert called_url.endswith("/_bulk")


def test_create_index_creates_index_if_missing_no_aws(create_module: Any) -> None:
    cio = create_module

    head_resp = MagicMock(status_code=404, text="", headers={}, reason="Not Found")
    put_resp = MagicMock(status_code=201, text="", headers={}, reason="Created")

    with (
        patch("create_open_search_index.sign_request_and_head", return_value=head_resp),
        patch("create_open_search_index.sign_request_and_put", return_value=put_resp),
    ):
        creator = cio.IndexCreator("https://endpoint.example", "index", "", None)
        assert creator.create_index() == 0


def test_create_index_then_populate_happy_path_no_aws(
    create_module: Any, create_populate_module: Any
) -> None:
    cio = create_module
    pop = create_populate_module

    head_resp = MagicMock(status_code=404, text="", headers={}, reason="Not Found")
    put_resp = MagicMock(status_code=201, text="", headers={}, reason="Created")

    bulk_resp = MagicMock()
    bulk_resp.status_code = 200
    bulk_resp.json.return_value = {"items": [{"index": {"status": 201}}]}

    with (
        patch("create_open_search_index.sign_request_and_head", return_value=head_resp),
        patch("create_open_search_index.sign_request_and_put", return_value=put_resp),
    ):
        creator = cio.IndexCreator("https://endpoint.example", "index", "", None)
        assert creator.create_index() == 0

    fake_session = MagicMock()
    fake_session.request.return_value = bulk_resp
    docs = [{"primary_key": "abc", pop.NESTED_COLLECTION_FIELD: []}]

    success, total = pop.index_records(
        fake_session,
        endpoint="https://endpoint.example",
        index_name="index",
        records=docs,
        batch_size=10,
    )

    assert (success, total) == (1, 1)
