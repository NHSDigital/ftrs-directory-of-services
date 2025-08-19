from unittest.mock import patch
from uuid import UUID

import pytest
from ftrs_data_layer.domain import (
    ClinicalCodeSource,
    ClinicalCodeType,
)
from ftrs_data_layer.domain import legacy as legacy_model

from pipeline.transformer.triage_code import TriageCodeTransformer


@pytest.fixture
def mock_generate_uuid() -> str:
    with patch("pipeline.transformer.triage_code.generate_uuid") as mock_uuid:
        mock_uuid.return_value = "31d5c731-1612-5041-9bc7-da3fe214e7a7"
        yield mock_uuid


pytestmark = pytest.mark.usefixtures("mock_generate_uuid")


def test_builds_triage_code_from_symptom_group_with_z_code() -> None:
    symptom_group = legacy_model.SymptomGroup(
        id="123", name="Test Symptom Group", zcodeexists=True
    )

    # Execute
    result = TriageCodeTransformer.build_triage_code_from_symptom_group(symptom_group)

    # Assert

    assert result.id == UUID("31d5c731-1612-5041-9bc7-da3fe214e7a7")
    assert result.source == ClinicalCodeSource.SERVICE_FINDER
    assert result.codeType == ClinicalCodeType.SYMPTOM_GROUP
    assert result.codeID == "123"
    assert result.codeValue == "Test Symptom Group"
    assert result.zCodeExists is True


def test_builds_triage_code_from_symptom_group_without_z_code() -> None:
    # Setup
    symptom_group = legacy_model.SymptomGroup(
        id="456", name="Another Symptom Group", zcodeexists=False
    )

    result = TriageCodeTransformer.build_triage_code_from_symptom_group(symptom_group)

    # Assert
    assert result.id == UUID("31d5c731-1612-5041-9bc7-da3fe214e7a7")
    assert result.source == ClinicalCodeSource.PATHWAYS
    assert result.codeType == ClinicalCodeType.SYMPTOM_GROUP
    assert result.codeID == "456"
    assert result.codeValue == "Another Symptom Group"
    assert result.zCodeExists is False


def test_builds_triage_code_from_disposition_with_time() -> None:
    # Setup
    disposition = legacy_model.Disposition(
        id="789", name="Test Disposition", dispositiontime=60
    )

    result = TriageCodeTransformer.build_triage_code_from_disposition(disposition)

    # Assert
    assert result.id == UUID("31d5c731-1612-5041-9bc7-da3fe214e7a7")
    assert result.source == ClinicalCodeSource.SERVICE_FINDER
    assert result.codeType == ClinicalCodeType.DISPOSITION
    assert result.codeID == "789"
    assert result.codeValue == "Test Disposition"
    assert result.time == disposition.dispositiontime


def test_builds_triage_code_from_disposition_without_time() -> None:
    # Setup
    disposition = legacy_model.Disposition(
        id="101", name="No Time Disposition", dispositiontime=None
    )

    result = TriageCodeTransformer.build_triage_code_from_disposition(disposition)

    # Assert
    assert result.id == UUID("31d5c731-1612-5041-9bc7-da3fe214e7a7")
    assert result.source == ClinicalCodeSource.SERVICE_FINDER
    assert result.codeType == ClinicalCodeType.DISPOSITION
    assert result.codeID == "101"
    assert result.codeValue == "No Time Disposition"
    assert result.time == 0


def test_builds_triage_code_from_symptom_discriminator_with_description() -> None:
    # Setup
    synonym1 = legacy_model.SymptomDiscriminatorSynonym(name="Synonym1")
    synonym2 = legacy_model.SymptomDiscriminatorSynonym(name="Synonym2")
    symptom_discriminator = legacy_model.SymptomDiscriminator(
        id="202", description="Test Description", synonyms=[synonym1, synonym2]
    )

    result = TriageCodeTransformer.build_triage_code_from_symptom_discriminator(
        symptom_discriminator
    )

    # Assert
    assert result.id == UUID("31d5c731-1612-5041-9bc7-da3fe214e7a7")
    assert result.source == ClinicalCodeSource.SERVICE_FINDER
    assert result.codeType == ClinicalCodeType.SYMPTOM_DISCRIMINATOR
    assert result.codeID == "202"
    assert result.codeValue == "Test Description"
    assert result.synonyms == ["Synonym1", "Synonym2"]


def test_builds_triage_code_from_symptom_discriminator_without_description() -> None:
    # Setup
    symptom_discriminator = legacy_model.SymptomDiscriminator(
        id="303", description=None, synonyms=[]
    )

    # Execute
    result = TriageCodeTransformer.build_triage_code_from_symptom_discriminator(
        symptom_discriminator
    )

    # Assert
    assert result.id == UUID("31d5c731-1612-5041-9bc7-da3fe214e7a7")
    assert result.source == ClinicalCodeSource.SERVICE_FINDER
    assert result.codeType == ClinicalCodeType.SYMPTOM_DISCRIMINATOR
    assert result.codeID == "303"
    assert result.codeValue == ""
    assert result.synonyms == []
