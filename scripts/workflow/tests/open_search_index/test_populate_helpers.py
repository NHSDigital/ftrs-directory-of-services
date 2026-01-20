from typing import Any

import pytest


def test_extract_field(create_populate_module: Any) -> None:
    mod = create_populate_module

    record = {
        "a": "s1",
        "b": 2,
        "c": "plain",
    }

    assert mod.extract_field(record, ("a", "b")) == "s1"
    assert mod.extract_field(record, ("b",)) == "2"
    assert mod.extract_field(record, ("c",)) == "plain"
    assert mod.extract_field(record, ("missing",)) is None


def test_extract_nested(create_populate_module: Any) -> None:
    mod = create_populate_module

    schema = mod.DEFAULT_SCHEMA_CONFIG.copy()

    nested_attr = [
        {"sg": "g1", "sd": "d1"},
        {"sg": "g2", "sd": "d2"},
    ]

    record = {"symptomGroupSymptomDiscriminators": nested_attr}

    items = mod.extract_nested_from_record(record, schema)
    assert isinstance(items, list)
    assert len(items) == 2
    assert items[0].get("sg") == "g1"
    assert items[0].get("sd") == "d1"


def test_parse_record(create_populate_module: Any) -> None:
    mod = create_populate_module

    top_fields = mod.TOP_LEVEL_OUTPUT_FIELDS
    if not top_fields:
        top_fields = [mod.PRIMARY_KEY_NAME] if mod.PRIMARY_KEY_NAME else []

    record = {}
    for fld in top_fields:
        record[fld] = f"v-{fld}"

    record["symptomGroupSymptomDiscriminators"] = [{"sg": "sgv", "sd": "sdv"}]

    doc = mod.parse_record_to_doc(record, mod.DEFAULT_SCHEMA_CONFIG)
    assert isinstance(doc, dict)
    for fld in top_fields:
        assert doc.get(fld) == f"v-{fld}"
    assert isinstance(doc.get(mod.NESTED_COLLECTION_FIELD), list)

    if top_fields:
        missing = dict(record)
        missing.pop(top_fields[0], None)
        assert mod.parse_record_to_doc(missing, mod.DEFAULT_SCHEMA_CONFIG) is None


def test_parse_record_reraise_on_value_error(
    create_populate_module: Any, monkeypatch: Any
) -> None:
    mod = create_populate_module

    def _raise_boom(*_args: Any, **_kwargs: Any) -> str:
        raise ValueError("boom")

    # Make extract_field raise a ValueError to simulate a parsing failure deep in the code
    monkeypatch.setattr(mod, "extract_field", _raise_boom)

    sample = {"id": "pk1", "symptomGroupSymptomDiscriminators": []}
    with pytest.raises(ValueError, match="boom"):
        mod.parse_record_to_doc(sample, mod.DEFAULT_SCHEMA_CONFIG)
