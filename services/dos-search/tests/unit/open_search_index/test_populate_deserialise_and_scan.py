from typing import Any
from unittest.mock import MagicMock


def test_deserialize_fallback_on_error(
    create_populate_module: Any, monkeypatch: Any
) -> None:
    mod = create_populate_module
    monkeypatch.setattr(
        mod,
        "_DESERIALIZER",
        MagicMock(deserialize=MagicMock(side_effect=TypeError("bad"))),
    )
    attr = {"S": "x"}
    res = mod._deserialize_attr(attr)
    assert res == attr


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


def test_convert_dynamodb_format_various(create_populate_module: Any) -> None:
    mod = create_populate_module
    items = [{"M": {"sg": {"N": "1"}, "sd": {"N": "2"}}}, {"S": "x"}]
    out = mod.convert_dynamodb_format(items)
    assert isinstance(out, list)
    assert out == []
