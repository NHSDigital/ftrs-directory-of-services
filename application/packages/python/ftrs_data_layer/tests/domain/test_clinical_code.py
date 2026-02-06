from uuid import uuid4

import pytest
from pydantic import ValidationError

from ftrs_data_layer.domain.clinical_code import (
    INVALID_CODE_TYPE,
    INVALID_CODE_TYPE_SD,
    INVALID_DISPOSITION_ITEM,
    INVALID_SG_SD_PAIR,
    BaseClinicalCode,
    Disposition,
    SymptomDiscriminator,
    SymptomGroup,
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.domain.enums import ClinicalCodeSource, ClinicalCodeType


class TestErrorConstants:
    """Tests for error message constants."""

    def test_invalid_disposition_item_constant(self) -> None:
        """Test INVALID_DISPOSITION_ITEM constant value."""
        assert INVALID_DISPOSITION_ITEM == "Each disposition item must be a JSON object"

    def test_invalid_sg_sd_pair_constant(self) -> None:
        """Test INVALID_SG_SD_PAIR constant value."""
        assert INVALID_SG_SD_PAIR == "Both 'sg' and 'sd' components are required in the pair"

    def test_invalid_code_type_constant(self) -> None:
        """Test INVALID_CODE_TYPE constant value."""
        assert INVALID_CODE_TYPE == "Invalid codeType for symptom group:"

    def test_invalid_code_type_sd_constant(self) -> None:
        """Test INVALID_CODE_TYPE_SD constant value."""
        assert INVALID_CODE_TYPE_SD == "Invalid codeType for symptom discriminator:"


class TestBaseClinicalCode:
    """Tests for BaseClinicalCode model."""

    def test_create_base_clinical_code(self) -> None:
        """Test creating BaseClinicalCode with all fields."""
        code_id = uuid4()
        clinical_code = BaseClinicalCode(
            id=code_id,
            source=ClinicalCodeSource.PATHWAYS,
            codeType=ClinicalCodeType.SYMPTOM_GROUP,
            codeID=1234,
            codeValue="SG1234",
        )

        assert clinical_code.id == code_id
        assert clinical_code.source == ClinicalCodeSource.PATHWAYS
        assert clinical_code.codeType == ClinicalCodeType.SYMPTOM_GROUP
        assert clinical_code.codeID == 1234
        assert clinical_code.codeValue == "SG1234"

    def test_create_base_clinical_code_with_string_code_id(self) -> None:
        """Test creating BaseClinicalCode with string codeID."""
        clinical_code = BaseClinicalCode(
            id=uuid4(),
            codeType=ClinicalCodeType.DISPOSITION,
            codeID="DX114",
        )

        assert clinical_code.codeID == "DX114"

    def test_base_clinical_code_optional_fields(self) -> None:
        """Test that optional fields default to None."""
        clinical_code = BaseClinicalCode(
            id=uuid4(),
            codeType=ClinicalCodeType.SYMPTOM_GROUP,
        )

        assert clinical_code.source is None
        assert clinical_code.codeID is None
        assert clinical_code.codeValue is None

    def test_base_clinical_code_with_service_finder_source(self) -> None:
        """Test creating BaseClinicalCode with SERVICE_FINDER source."""
        clinical_code = BaseClinicalCode(
            id=uuid4(),
            source=ClinicalCodeSource.SERVICE_FINDER,
            codeType=ClinicalCodeType.SG_SD_PAIR,
        )

        assert clinical_code.source == ClinicalCodeSource.SERVICE_FINDER

    def test_base_clinical_code_model_dump_json(self) -> None:
        """Test BaseClinicalCode serialization to JSON."""
        code_id = uuid4()
        clinical_code = BaseClinicalCode(
            id=code_id,
            source=ClinicalCodeSource.PATHWAYS,
            codeType=ClinicalCodeType.SYMPTOM_DISCRIMINATOR,
            codeID=5678,
            codeValue="SD5678",
        )

        dumped = clinical_code.model_dump(mode="json")

        assert dumped["id"] == str(code_id)
        assert dumped["source"] == "pathways"
        assert dumped["codeType"] == "Symptom Discriminator (SD)"
        assert dumped["codeID"] == 5678
        assert dumped["codeValue"] == "SD5678"


class TestSymptomGroup:
    """Tests for SymptomGroup model."""

    def test_create_symptom_group(self) -> None:
        """Test creating SymptomGroup."""
        sg = SymptomGroup(
            id=uuid4(),
            source=ClinicalCodeSource.PATHWAYS,
            codeID=1000,
            codeValue="Chest Pain",
        )

        assert sg.codeType == ClinicalCodeType.SYMPTOM_GROUP
        assert sg.codeID == 1000
        assert sg.codeValue == "Chest Pain"

    def test_symptom_group_default_code_type(self) -> None:
        """Test that SymptomGroup has default codeType of SYMPTOM_GROUP."""
        sg = SymptomGroup(id=uuid4())

        assert sg.codeType == ClinicalCodeType.SYMPTOM_GROUP

    def test_symptom_group_model_dump_json(self) -> None:
        """Test SymptomGroup serialization to JSON."""
        sg = SymptomGroup(
            id=uuid4(),
            source=ClinicalCodeSource.PATHWAYS,
            codeID=2000,
            codeValue="Headache",
        )

        dumped = sg.model_dump(mode="json")

        assert dumped["codeType"] == "Symptom Group (SG)"
        assert dumped["source"] == "pathways"


class TestSymptomDiscriminator:
    """Tests for SymptomDiscriminator model."""

    def test_create_symptom_discriminator(self) -> None:
        """Test creating SymptomDiscriminator."""
        sd = SymptomDiscriminator(
            id=uuid4(),
            source=ClinicalCodeSource.PATHWAYS,
            codeID=4003,
            codeValue="Severe pain",
        )

        assert sd.codeType == ClinicalCodeType.SYMPTOM_DISCRIMINATOR
        assert sd.codeID == 4003
        assert sd.codeValue == "Severe pain"

    def test_symptom_discriminator_with_synonyms(self) -> None:
        """Test creating SymptomDiscriminator with synonyms."""
        sd = SymptomDiscriminator(
            id=uuid4(),
            codeID=4003,
            synonyms=["intense pain", "strong pain", "unbearable pain"],
        )

        assert sd.synonyms == ["intense pain", "strong pain", "unbearable pain"]

    def test_symptom_discriminator_default_synonyms(self) -> None:
        """Test that SymptomDiscriminator has empty list as default synonyms."""
        sd = SymptomDiscriminator(id=uuid4())

        assert sd.synonyms == []

    def test_symptom_discriminator_model_dump_json(self) -> None:
        """Test SymptomDiscriminator serialization to JSON."""
        sd = SymptomDiscriminator(
            id=uuid4(),
            codeID=5000,
            synonyms=["synonym1", "synonym2"],
        )

        dumped = sd.model_dump(mode="json")

        assert dumped["codeType"] == "Symptom Discriminator (SD)"
        assert dumped["synonyms"] == ["synonym1", "synonym2"]


class TestDisposition:
    """Tests for Disposition model."""

    def test_create_disposition(self) -> None:
        """Test creating Disposition."""
        disposition = Disposition(
            id=uuid4(),
            source=ClinicalCodeSource.PATHWAYS,
            codeID="DX114",
            codeValue="Attend ED within 4 hours",
        )

        assert disposition.codeType == ClinicalCodeType.DISPOSITION
        assert disposition.codeID == "DX114"
        assert disposition.codeValue == "Attend ED within 4 hours"

    def test_disposition_with_time(self) -> None:
        """Test creating Disposition with time field."""
        disposition = Disposition(
            id=uuid4(),
            codeID="DX114",
            time=240,
        )

        assert disposition.time == 240

    def test_disposition_default_time(self) -> None:
        """Test that Disposition has default time of 0."""
        disposition = Disposition(id=uuid4())

        assert disposition.time == 0

    def test_disposition_model_dump_json(self) -> None:
        """Test Disposition serialization to JSON."""
        disposition = Disposition(
            id=uuid4(),
            codeID="DX01",
            codeValue="Contact ambulance immediately",
            time=0,
        )

        dumped = disposition.model_dump(mode="json")

        assert dumped["codeType"] == "Disposition (Dx)"
        assert dumped["time"] == 0


class TestSymptomGroupSymptomDiscriminatorPair:
    """Tests for SymptomGroupSymptomDiscriminatorPair model."""

    def test_create_sg_sd_pair(self) -> None:
        """Test creating SymptomGroupSymptomDiscriminatorPair."""
        pair = SymptomGroupSymptomDiscriminatorPair(sg=1000, sd=4003)

        assert pair.sg == 1000
        assert pair.sd == 4003

    def test_sg_sd_pair_model_dump_json(self) -> None:
        """Test SymptomGroupSymptomDiscriminatorPair serialization to JSON."""
        pair = SymptomGroupSymptomDiscriminatorPair(sg=2000, sd=5000)

        dumped = pair.model_dump(mode="json")

        assert dumped == {"sg": 2000, "sd": 5000}

    def test_sg_sd_pair_missing_sg_raises_error(self) -> None:
        """Test that missing sg raises ValidationError."""
        with pytest.raises(ValidationError):
            SymptomGroupSymptomDiscriminatorPair(sd=4003)  # type: ignore

    def test_sg_sd_pair_missing_sd_raises_error(self) -> None:
        """Test that missing sd raises ValidationError."""
        with pytest.raises(ValidationError):
            SymptomGroupSymptomDiscriminatorPair(sg=1000)  # type: ignore

    def test_sg_sd_pair_round_trip(self) -> None:
        """Test SymptomGroupSymptomDiscriminatorPair round trip."""
        original = SymptomGroupSymptomDiscriminatorPair(sg=3000, sd=6000)

        dumped = original.model_dump(mode="json")
        reloaded = SymptomGroupSymptomDiscriminatorPair.model_validate(dumped)

        assert reloaded.sg == original.sg
        assert reloaded.sd == original.sd

    def test_sg_sd_pair_with_zero_values(self) -> None:
        """Test creating pair with zero values."""
        pair = SymptomGroupSymptomDiscriminatorPair(sg=0, sd=0)

        assert pair.sg == 0
        assert pair.sd == 0

    def test_sg_sd_pair_with_large_values(self) -> None:
        """Test creating pair with large integer values."""
        pair = SymptomGroupSymptomDiscriminatorPair(sg=999999, sd=888888)

        assert pair.sg == 999999
        assert pair.sd == 888888
