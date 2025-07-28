import json
from json import JSONDecodeError

import numpy as np
import pydantic_core
import pytest
from ftrs_data_layer.domain.clinical_code import (
    ClinicalCodeConverter,
    Disposition,
    SymptomDiscriminator,
    SymptomGroup,
)


def test_converts_valid_sg_sd_pair_string() -> None:
    sg_sd_pair = '{"sg": {"id": "1", "source": "pathways", "codeType": "Symptom Group (SG)", "codeID": 101, "codeValue": "SG1", "zCodeExists": true}, "sd": {"id": "2", "source": "pathways", "codeType": "Symptom Discriminator (SD)", "codeID": 201, "codeValue": "SD1", "synonyms": ["syn1", "syn2"]}}'
    result = ClinicalCodeConverter.convert_sg_sd_pair(sg_sd_pair)
    assert result.SG_SD[0]["sg"].id == "1"
    assert result.SG_SD[0]["sd"].id == "2"
    assert result.SG_SD[0]["sg"] == SymptomGroup(
        id="1",
        source="pathways",
        codeType="Symptom Group (SG)",
        codeID=101,
        codeValue="SG1",
        zCodeExists=True,
    )
    assert result.SG_SD[0]["sd"] == SymptomDiscriminator(
        id="2",
        source="pathways",
        codeType="Symptom Discriminator (SD)",
        codeID=201,
        codeValue="SD1",
        synonyms=["syn1", "syn2"],
    )


def test_raises_error_for_invalid_json_string() -> None:
    sg_sd_pair = '{"sg": {"id": "1", "source": "pathways", "codeType": "Symptom Group (SG)", "codeID": 101, "codeValue": "SG1", "zCodeExists": true}, "sd": {"id": "2", "source": "pathways", "codeType": "Symptom Discriminator (SD)", "codeID": 201, "codeValue": "SD1", "synonyms": ["syn1", "syn2"]}'
    with pytest.raises(
        JSONDecodeError, match="Expecting ',' delimiter: line 1 column 279"
    ):
        ClinicalCodeConverter.convert_sg_sd_pair(sg_sd_pair)


def test_raises_error_for_missing_sg_or_sd() -> None:
    sg_sd_pair = '{"sg": {"id": "1", "source": "pathways", "codeType": "Symptom Group (SG)", "codeID": 101, "codeValue": "SG1", "zCodeExists": true}}'
    with pytest.raises(ValueError, match="Both 'sg' and 'sd' components are required"):
        ClinicalCodeConverter.convert_sg_sd_pair(sg_sd_pair)


def test_raises_error_for_invalid_codeType_in_sg() -> None:
    sg_sd_pair = '{"sg": {"id": "1", "source": "pathways", "codeType": "Invalid Type", "codeID": 101, "codeValue": "SG1", "zCodeExists": true}, "sd": {"id": "2", "source": "pathways", "codeType": "Symptom Discriminator (SD)", "codeID": 201, "codeValue": "SD1", "synonyms": ["syn1", "syn2"]}}'
    with pytest.raises(
        TypeError, match="Invalid codeType for symptom group:Invalid Type"
    ):
        ClinicalCodeConverter.convert_sg_sd_pair(sg_sd_pair)


def test_raises_error_for_invalid_codeType_in_sd() -> None:
    sg_sd_pair = '{"sg": {"id": "1", "source": "pathways", "codeType": "Symptom Group (SG)", "codeID": 101, "codeValue": "SG1", "zCodeExists": true}, "sd": {"id": "2", "source": "pathways", "codeType": "Invalid Type", "codeID": 201, "codeValue": "SD1", "synonyms": ["syn1", "syn2"]}}'
    with pytest.raises(
        TypeError, match="Invalid codeType for symptom discriminator:Invalid Type"
    ):
        ClinicalCodeConverter.convert_sg_sd_pair(sg_sd_pair)


def test_converts_valid_sg_sd_pair_ndarray() -> None:
    sg_sd_pair = np.array(
        [
            '{"sg": {"id": "1", "source": "pathways", "codeType": "Symptom Group (SG)", "codeID": 101, "codeValue": "SG1", "zCodeExists": true}, "sd": {"id": "2", "source": "pathways", "codeType": "Symptom Discriminator (SD)", "codeID": 201, "codeValue": "SD1", "synonyms": ["syn1", "syn2"]}}'
        ]
    )
    result = ClinicalCodeConverter.convert_sg_sd_pair(sg_sd_pair)
    assert result.SG_SD[0]["sg"].id == "1"
    assert result.SG_SD[0]["sd"].id == "2"


def test_converts_valid_dispositions_string() -> None:
    dispositions = '[{"id": "1", "source": "pathways", "codeType": "Disposition (Dx)", "codeID": 301, "codeValue": "Dx1", "dispositiontime": 10}]'
    result = ClinicalCodeConverter.convert_dispositions(dispositions)

    assert len(result) == 1
    assert result[0] == Disposition(
        id="1",
        source="pathways",
        codeType="Disposition (Dx)",
        codeID=301,
        codeValue="Dx1",
        time=10,
    )


def test_converts_valid_dispositions_ndarray() -> None:
    dispositions = np.array(
        [
            '{"id": "1", "source": "pathways", "codeType": "Disposition (Dx)", "codeID": 301, "codeValue": "Dx1", "dispositiontime": 10}'
        ]
    )
    result = ClinicalCodeConverter.convert_dispositions(dispositions)
    assert len(result) == 1
    assert result[0] == Disposition(
        id="1",
        source="pathways",
        codeType="Disposition (Dx)",
        codeID=301,
        codeValue="Dx1",
        time=10,
    )


def test_raises_error_for_invalid_json_string_in_dispositions() -> None:
    dispositions = '[{"id": "1", "source": "pathways", "codeType": "Disposition (Dx)", "codeID": 301, "codeValue": "Dx1", "time": 10}'
    with pytest.raises(
        JSONDecodeError, match="Expecting ',' delimiter: line 1 column 114"
    ):
        ClinicalCodeConverter.convert_dispositions(dispositions)


def test_raises_error_for_invalid_disposition_format() -> None:
    dispositions = '[{"id": "1", "source": "pathways", "codeType": "Disposition (Dx)", "codeID": 301, "codeValue": "Dx1", "time": 10}, "invalid_format"]'
    with pytest.raises(TypeError, match="Each disposition item must be a JSON object"):
        ClinicalCodeConverter.convert_dispositions(dispositions)


def test_raises_error_for_missing_required_fields_in_disposition() -> None:
    dispositions = '[{"source": "pathways", "codeType": "Disposition (Dx)", "codeID": 301, "codeValue": "Dx1"}]'
    with pytest.raises(
        pydantic_core._pydantic_core.ValidationError,
        match="1 validation error for Disposition",
    ):
        ClinicalCodeConverter.convert_dispositions(dispositions)
