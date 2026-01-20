from typing import Any
from unittest.mock import MagicMock


def test_deserialize_item_fallback_on_error(
    create_populate_module: Any, monkeypatch: Any
) -> None:
    mod = create_populate_module
    monkeypatch.setattr(
        mod,
        "_DESERIALIZER",
        MagicMock(deserialize=MagicMock(side_effect=TypeError("bad"))),
    )
    # DynamoDB client items use AttributeValue shapes; deserialize_dynamodb_item wraps
    # the item as {"M": item} and should return None on deserialization errors.
    item = {"id": {"S": "x"}}
    assert mod.deserialize_dynamodb_item(item) is None


def test_scan_dynamodb_table_pagination(create_populate_module: Any) -> None:
    mod = create_populate_module

    class Client:
        @staticmethod
        def get_paginator(_name):
            class P:
                @staticmethod
                def paginate(**kwargs):
                    # consume kwargs to avoid unused-parameter warnings
                    _ = kwargs
                    yield {"Items": [{"a": 1}]}

            return P()

    items = mod.scan_dynamodb_table(Client(), "table", ["a", "b"])
    assert isinstance(items, list)
    assert any("a" in itm or "b" in itm for itm in items)


def test_deserialize_dynamodb_items_filters_invalid(create_populate_module: Any) -> None:
    mod = create_populate_module
    items = [
        {"id": {"S": "x"}},
        "not-a-dict",
    ]
    out = mod.deserialize_dynamodb_items(items)  # type: ignore[arg-type]
    assert isinstance(out, list)
    assert out == [{"id": "x"}]
