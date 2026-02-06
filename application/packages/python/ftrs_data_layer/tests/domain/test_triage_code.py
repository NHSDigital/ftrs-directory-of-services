from uuid import uuid4

import pytest
from pydantic import ValidationError

from ftrs_data_layer.domain.enums import ClinicalCodeSource, ClinicalCodeType
from ftrs_data_layer.domain.triage_code import TriageCode, TriageCodeCombination


class TestTriageCodeCombination:
    """Tests for TriageCodeCombination model."""

    def test_create_triage_code_combination(self) -> None:
        """Test creating TriageCodeCombination with required fields."""
        combination = TriageCodeCombination(
            value="SG1000-SD4003",
            id="combo-123",
        )

        assert combination.value == "SG1000-SD4003"
        assert combination.id == "combo-123"

    def test_triage_code_combination_model_dump_json(self) -> None:
        """Test TriageCodeCombination serialization to JSON."""
        combination = TriageCodeCombination(
            value="DX114-SG2000",
            id="combo-456",
        )

        dumped = combination.model_dump(mode="json")

        assert dumped == {
            "value": "DX114-SG2000",
            "id": "combo-456",
        }

    def test_triage_code_combination_round_trip(self) -> None:
        """Test TriageCodeCombination serialization and deserialization."""
        original = TriageCodeCombination(
            value="test-value",
            id="test-id",
        )

        dumped = original.model_dump(mode="json")
        reloaded = TriageCodeCombination.model_validate(dumped)

        assert reloaded.value == original.value
        assert reloaded.id == original.id

    def test_triage_code_combination_missing_value_raises_error(self) -> None:
        """Test that missing value raises ValidationError."""
        with pytest.raises(ValidationError):
            TriageCodeCombination(id="test-id")  # type: ignore

    def test_triage_code_combination_missing_id_raises_error(self) -> None:
        """Test that missing id raises ValidationError."""
        with pytest.raises(ValidationError):
            TriageCodeCombination(value="test-value")  # type: ignore

    def test_triage_code_combination_with_empty_strings(self) -> None:
        """Test creating TriageCodeCombination with empty strings."""
        combination = TriageCodeCombination(
            value="",
            id="",
        )

        assert combination.value == ""
        assert combination.id == ""


class TestTriageCode:
    """Tests for TriageCode model."""

    def test_create_triage_code(self) -> None:
        """Test creating TriageCode with all fields."""
        triage_code = TriageCode(
            id="TC-001",
            source=ClinicalCodeSource.PATHWAYS,
            codeType=ClinicalCodeType.SYMPTOM_GROUP,
            codeID=1000,
            codeValue="Chest Pain",
            field="symptomGroup",
        )

        assert triage_code.id == "TC-001"
        assert triage_code.source == ClinicalCodeSource.PATHWAYS
        assert triage_code.codeType == ClinicalCodeType.SYMPTOM_GROUP
        assert triage_code.codeID == 1000
        assert triage_code.codeValue == "Chest Pain"
        assert triage_code.field == "symptomGroup"

    def test_triage_code_with_default_field(self) -> None:
        """Test that TriageCode has default field value."""
        triage_code = TriageCode(
            id="TC-002",
            codeType=ClinicalCodeType.SYMPTOM_DISCRIMINATOR,
        )

        assert triage_code.field == "item"

    def test_triage_code_with_synonyms(self) -> None:
        """Test creating TriageCode with synonyms list."""
        triage_code = TriageCode(
            id="TC-003",
            codeType=ClinicalCodeType.SYMPTOM_DISCRIMINATOR,
            synonyms=["pain", "ache", "discomfort"],
        )

        assert triage_code.synonyms == ["pain", "ache", "discomfort"]

    def test_triage_code_default_synonyms(self) -> None:
        """Test that TriageCode has empty list as default synonyms."""
        triage_code = TriageCode(
            id="TC-004",
            codeType=ClinicalCodeType.DISPOSITION,
        )

        assert triage_code.synonyms == []

    def test_triage_code_with_time(self) -> None:
        """Test creating TriageCode with time field."""
        triage_code = TriageCode(
            id="TC-005",
            codeType=ClinicalCodeType.DISPOSITION,
            time=240,
        )

        assert triage_code.time == 240

    def test_triage_code_default_time(self) -> None:
        """Test that TriageCode has default time of 0."""
        triage_code = TriageCode(
            id="TC-006",
            codeType=ClinicalCodeType.DISPOSITION,
        )

        assert triage_code.time == 0

    def test_triage_code_with_zcode_exists(self) -> None:
        """Test creating TriageCode with zCodeExists flag."""
        triage_code = TriageCode(
            id="TC-007",
            codeType=ClinicalCodeType.SYMPTOM_GROUP,
            zCodeExists=True,
        )

        assert triage_code.zCodeExists is True

    def test_triage_code_default_zcode_exists(self) -> None:
        """Test that TriageCode has default zCodeExists of False."""
        triage_code = TriageCode(
            id="TC-008",
            codeType=ClinicalCodeType.SYMPTOM_GROUP,
        )

        assert triage_code.zCodeExists is False

    def test_triage_code_with_combinations(self) -> None:
        """Test creating TriageCode with combinations list."""
        combinations = [
            TriageCodeCombination(value="combo1", id="c1"),
            TriageCodeCombination(value="combo2", id="c2"),
        ]

        triage_code = TriageCode(
            id="TC-009",
            codeType=ClinicalCodeType.SG_SD_PAIR,
            combinations=combinations,
        )

        assert len(triage_code.combinations) == 2
        assert triage_code.combinations[0].value == "combo1"
        assert triage_code.combinations[1].id == "c2"

    def test_triage_code_default_combinations(self) -> None:
        """Test that TriageCode has empty list as default combinations."""
        triage_code = TriageCode(
            id="TC-010",
            codeType=ClinicalCodeType.SYMPTOM_GROUP,
        )

        assert triage_code.combinations == []

    def test_triage_code_with_dx_group_ids(self) -> None:
        """Test creating TriageCode with dx_group_ids list."""
        triage_code = TriageCode(
            id="TC-011",
            codeType=ClinicalCodeType.DISPOSITION,
            dx_group_ids=[1, 2, 3, 4],
        )

        assert triage_code.dx_group_ids == [1, 2, 3, 4]

    def test_triage_code_default_dx_group_ids(self) -> None:
        """Test that TriageCode has empty list as default dx_group_ids."""
        triage_code = TriageCode(
            id="TC-012",
            codeType=ClinicalCodeType.DISPOSITION,
        )

        assert triage_code.dx_group_ids == []

    def test_triage_code_model_dump_json(self) -> None:
        """Test TriageCode serialization to JSON."""
        triage_code = TriageCode(
            id="TC-013",
            source=ClinicalCodeSource.SERVICE_FINDER,
            codeType=ClinicalCodeType.SYMPTOM_GROUP,
            codeID=5000,
            codeValue="Test Symptom",
            field="testField",
            synonyms=["syn1"],
            time=60,
            zCodeExists=True,
            combinations=[TriageCodeCombination(value="v1", id="i1")],
            dx_group_ids=[10, 20],
        )

        dumped = triage_code.model_dump(mode="json")

        assert dumped["id"] == "TC-013"
        assert dumped["source"] == "servicefinder"
        assert dumped["codeType"] == "Symptom Group (SG)"
        assert dumped["codeID"] == 5000
        assert dumped["codeValue"] == "Test Symptom"
        assert dumped["field"] == "testField"
        assert dumped["synonyms"] == ["syn1"]
        assert dumped["time"] == 60
        assert dumped["zCodeExists"] is True
        assert len(dumped["combinations"]) == 1
        assert dumped["dx_group_ids"] == [10, 20]

    def test_triage_code_inherits_from_db_model(self) -> None:
        """Test that TriageCode inherits DBModel fields."""
        triage_code = TriageCode(
            id="TC-014",
            codeType=ClinicalCodeType.DISPOSITION,
        )

        # DBModel fields should be present
        assert hasattr(triage_code, "createdTime")
        assert hasattr(triage_code, "lastUpdated")
        assert hasattr(triage_code, "createdBy")
        assert hasattr(triage_code, "lastUpdatedBy")

    def test_triage_code_inherits_from_base_clinical_code(self) -> None:
        """Test that TriageCode inherits BaseClinicalCode fields."""
        triage_code = TriageCode(
            id="TC-015",
            source=ClinicalCodeSource.PATHWAYS,
            codeType=ClinicalCodeType.SYMPTOM_DISCRIMINATOR,
            codeID=9000,
            codeValue="Test Value",
        )

        # BaseClinicalCode fields
        assert triage_code.source == ClinicalCodeSource.PATHWAYS
        assert triage_code.codeType == ClinicalCodeType.SYMPTOM_DISCRIMINATOR
        assert triage_code.codeID == 9000
        assert triage_code.codeValue == "Test Value"

    def test_triage_code_round_trip(self) -> None:
        """Test TriageCode serialization and deserialization."""
        original = TriageCode(
            id="TC-016",
            codeType=ClinicalCodeType.DISPOSITION,
            codeID=100,
            field="testField",
            synonyms=["a", "b"],
            time=120,
            zCodeExists=False,
            dx_group_ids=[5],
        )

        dumped = original.model_dump(mode="json")
        reloaded = TriageCode.model_validate(dumped)

        assert reloaded.id == original.id
        assert reloaded.field == original.field
        assert reloaded.synonyms == original.synonyms
        assert reloaded.time == original.time
        assert reloaded.zCodeExists == original.zCodeExists
        assert reloaded.dx_group_ids == original.dx_group_ids

    def test_triage_code_with_null_field(self) -> None:
        """Test creating TriageCode with null field."""
        triage_code = TriageCode(
            id="TC-017",
            codeType=ClinicalCodeType.DISPOSITION,
            field=None,
        )

        assert triage_code.field is None

    def test_triage_code_with_null_time(self) -> None:
        """Test creating TriageCode with null time."""
        triage_code = TriageCode(
            id="TC-018",
            codeType=ClinicalCodeType.DISPOSITION,
            time=None,
        )

        assert triage_code.time is None

    def test_triage_code_with_null_zcode_exists(self) -> None:
        """Test creating TriageCode with null zCodeExists."""
        triage_code = TriageCode(
            id="TC-019",
            codeType=ClinicalCodeType.SYMPTOM_GROUP,
            zCodeExists=None,
        )

        assert triage_code.zCodeExists is None
