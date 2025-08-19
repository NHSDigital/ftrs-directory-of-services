from ftrs_data_layer.domain import (
    ClinicalCodeSource,
    ClinicalCodeType,
)
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.domain.triage_code import TriageCodeCombination

from pipeline.transformer.triage_code import TriageCodeTransformer


def test_builds_triage_code_from_symptom_group_with_z_code() -> None:
    symptom_group = legacy_model.SymptomGroup(
        id="123", name="Test Symptom Group", zcodeexists=True
    )

    # Execute
    result = TriageCodeTransformer.build_triage_code_from_symptom_group(symptom_group)

    # Assert

    assert result.id == "SG123"
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
    assert result.id == "SG456"
    assert result.source == ClinicalCodeSource.PATHWAYS
    assert result.codeType == ClinicalCodeType.SYMPTOM_GROUP
    assert result.codeID == "456"
    assert result.codeValue == "Another Symptom Group"
    assert result.zCodeExists is False


def test_builds_triage_code_from_disposition_with_time() -> None:
    # Setup
    disposition = legacy_model.Disposition(
        id="789", name="Test Disposition", dispositiontime=60, dxcode="DX789"
    )

    result = TriageCodeTransformer.build_triage_code_from_disposition(disposition)

    # Assert
    assert result.id == "DX789"
    assert result.codeType == ClinicalCodeType.DISPOSITION
    assert result.codeID == "DX789"
    assert result.codeValue == "Test Disposition"
    assert result.time == disposition.dispositiontime


def test_builds_triage_code_from_disposition_without_time() -> None:
    # Setup
    disposition = legacy_model.Disposition(
        id="101", name="No Time Disposition", dispositiontime=None, dxcode="DX101"
    )

    result = TriageCodeTransformer.build_triage_code_from_disposition(disposition)

    # Assert
    assert result.id == "DX101"
    assert result.codeType == ClinicalCodeType.DISPOSITION
    assert result.codeID == "DX101"
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
    assert result.id == "SD202"
    assert result.source == ClinicalCodeSource.PATHWAYS
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
    assert result.id == "SD303"
    assert result.source == ClinicalCodeSource.PATHWAYS
    assert result.codeType == ClinicalCodeType.SYMPTOM_DISCRIMINATOR
    assert result.codeID == "303"
    assert result.codeValue == ""
    assert result.synonyms == []


def test_builds_triage_code_combinations() -> None:
    # Setup
    sg = legacy_model.SymptomGroup(id="1", name="SG1", zcodeexists=True)
    sd = legacy_model.SymptomDiscriminator(
        id="2", description="Symptom Discriminator description", synonyms=[]
    )
    sg_sd = [
        legacy_model.SymptomGroupSymptomDiscriminator(
            id=123,
            symptomgroupid=sg.id,
            symptomdiscriminatorid=sd.id,
            symptomgroup=sg,
            symptomdiscriminator=sd,
        )
    ]

    result = TriageCodeTransformer.build_triage_code_combinations(1, sg_sd)
    assert result.field == "combinations"
    assert result.id == "SG1"
    assert result.codeType == ClinicalCodeType.SG_SD_PAIR
    assert result.combinations == [
        TriageCodeCombination(value="Symptom Discriminator description", id="SD2")
    ]


def test_builds_triage_code_combinations_empty_list() -> None:
    # Setup
    result = TriageCodeTransformer.build_triage_code_combinations(1, [])

    # Assert
    assert result.id == "SG1"
    assert result.combinations == []
    assert result.field == "combinations"


def test_builds_triage_code_from_symptom_discriminator_with_varied_sources() -> None:
    # Setup for PATHWAYS source
    symptom_discriminator_pathways = legacy_model.SymptomDiscriminator(
        id=100, description="Test Description", synonyms=[]
    )
    result_pathways = (
        TriageCodeTransformer.build_triage_code_from_symptom_discriminator(
            symptom_discriminator_pathways
        )
    )

    # Assert for PATHWAYS source
    assert result_pathways.source == ClinicalCodeSource.PATHWAYS

    # Setup for SERVICE_FINDER source
    symptom_discriminator_service_finder = legacy_model.SymptomDiscriminator(
        id=11000, description="Test Description", synonyms=[]
    )
    result_service_finder = (
        TriageCodeTransformer.build_triage_code_from_symptom_discriminator(
            symptom_discriminator_service_finder
        )
    )

    # Assert for SERVICE_FINDER source
    assert result_service_finder.source == ClinicalCodeSource.SERVICE_FINDER
