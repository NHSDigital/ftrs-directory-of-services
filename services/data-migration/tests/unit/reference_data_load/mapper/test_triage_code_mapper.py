from ftrs_data_layer.domain import (
    ClinicalCodeSource,
    ClinicalCodeType,
)
from ftrs_data_layer.domain.legacy.data_models import (
    DispositionData,
    SymptomDiscriminatorData,
    SymptomDiscriminatorSynonymData,
    SymptomGroupData,
)
from ftrs_data_layer.domain.triage_code import TriageCodeCombination

from reference_data_load.mapper.triage_code_mapper import (
    DispositionMapper,
    SGSDCombinationMapper,
    SymptomDiscriminatorMapper,
    SymptomGroupMapper,
)


def test_builds_triage_code_from_symptom_group_with_z_code() -> None:
    symptom_group_id = 123
    symptom_group = SymptomGroupData(
        id=symptom_group_id,
        name="Test Symptom Group",
        zcodeexists=True,
    )

    # Execute
    result = SymptomGroupMapper().map(symptom_group)

    # Assert

    assert result.id == "SG123"
    assert result.source == ClinicalCodeSource.SERVICE_FINDER
    assert result.codeType == ClinicalCodeType.SYMPTOM_GROUP
    assert result.codeID == symptom_group_id
    assert result.codeValue == "Test Symptom Group"
    assert result.zCodeExists is True


def test_builds_triage_code_from_symptom_group_without_z_code() -> None:
    # Setup
    symptom_group_id = 456
    symptom_group = SymptomGroupData(
        id=symptom_group_id,
        name="Another Symptom Group",
        zcodeexists=False,
    )

    result = SymptomGroupMapper().map(symptom_group)

    # Assert
    assert result.id == "SG456"
    assert result.source == ClinicalCodeSource.PATHWAYS
    assert result.codeType == ClinicalCodeType.SYMPTOM_GROUP
    assert result.codeID == symptom_group_id
    assert result.codeValue == "Another Symptom Group"
    assert result.zCodeExists is False


def test_builds_triage_code_from_disposition_with_time() -> None:
    # Setup
    disposition_id = 789
    disposition = DispositionData(
        id=disposition_id,
        name="Test Disposition",
        dispositiontime=60,
        dxcode="DX789",
    )

    result = DispositionMapper().map(disposition)

    # Assert
    assert result.id == "DX789"
    assert result.source == ClinicalCodeSource.PATHWAYS
    assert result.codeType == ClinicalCodeType.DISPOSITION
    assert result.codeID == f"DX{disposition_id}"
    assert result.codeValue == "Test Disposition"
    assert result.time == disposition.dispositiontime


def test_builds_triage_code_from_disposition_without_time() -> None:
    # Setup
    disposition_id = 101
    disposition = DispositionData(
        id=disposition_id,
        name="No Time Disposition",
        dispositiontime=None,
        dxcode="DX101",
    )

    result = DispositionMapper().map(disposition)

    # Assert
    assert result.id == "DX101"
    assert result.source == ClinicalCodeSource.PATHWAYS
    assert result.codeType == ClinicalCodeType.DISPOSITION
    assert result.codeID == f"DX{disposition_id}"
    assert result.codeValue == "No Time Disposition"
    assert result.time == 0


def test_builds_triage_code_from_symptom_discriminator_with_description() -> None:
    # Setup
    synonym1 = SymptomDiscriminatorSynonymData(
        id=1,
        name="Synonym1",
        symptomdiscriminatorid=202,
    )
    synonym2 = SymptomDiscriminatorSynonymData(
        id=2,
        name="Synonym2",
        symptomdiscriminatorid=202,
    )

    symptom_discriminator_id = 202
    symptom_discriminator = SymptomDiscriminatorData(
        id=symptom_discriminator_id,
        description="Test Description",
        synonyms=[synonym1, synonym2],
    )

    result = SymptomDiscriminatorMapper().map(symptom_discriminator)

    # Assert
    assert result.id == "SD202"
    assert result.source == ClinicalCodeSource.PATHWAYS
    assert result.codeType == ClinicalCodeType.SYMPTOM_DISCRIMINATOR
    assert result.codeID == symptom_discriminator_id
    assert result.codeValue == "Test Description"

    assert result.synonyms == ["Synonym1", "Synonym2"]


def test_builds_triage_code_from_symptom_discriminator_without_description() -> None:
    # Setup
    symptom_discriminator_id = 303
    symptom_discriminator = SymptomDiscriminatorData(
        id=symptom_discriminator_id,
        description=None,
        synonyms=[],
    )

    # Execute
    result = SymptomDiscriminatorMapper().map(symptom_discriminator)

    # Assert
    assert result.id == "SD303"
    assert result.source == ClinicalCodeSource.PATHWAYS
    assert result.codeType == ClinicalCodeType.SYMPTOM_DISCRIMINATOR
    assert result.codeID == symptom_discriminator_id
    assert result.codeValue == ""
    assert result.synonyms == []


def test_builds_triage_code_combinations() -> None:
    # Setup
    sg = SymptomGroupData(id="1", name="SG1", zcodeexists=True)
    sd = SymptomDiscriminatorData(
        id="2", description="Symptom Discriminator description", synonyms=[]
    )

    result = SGSDCombinationMapper().map(sg, [sd])
    assert result.field == "combinations"
    assert result.id == "SG1"
    assert result.codeType == ClinicalCodeType.SG_SD_PAIR
    assert result.combinations == [
        TriageCodeCombination(value="Symptom Discriminator description", id="SD2")
    ]


def test_builds_triage_code_combinations_empty_list() -> None:
    # Setup
    sg = SymptomGroupData(id="1", name="SG1", zcodeexists=True)
    result = SGSDCombinationMapper().map(sg, [])

    # Assert
    assert result.id == "SG1"
    assert result.combinations == []
    assert result.field == "combinations"


def test_builds_triage_code_from_symptom_discriminator_with_varied_sources() -> None:
    # Setup for PATHWAYS source
    symptom_discriminator_pathways = SymptomDiscriminatorData(
        id=100, description="Test Description", synonyms=[]
    )
    result_pathways = SymptomDiscriminatorMapper().map(symptom_discriminator_pathways)

    # Assert for PATHWAYS source
    assert result_pathways.source == ClinicalCodeSource.PATHWAYS

    # Setup for SERVICE_FINDER source
    symptom_discriminator_service_finder = SymptomDiscriminatorData(
        id=11000, description="Test Description", synonyms=[]
    )
    result_service_finder = SymptomDiscriminatorMapper().map(
        symptom_discriminator_service_finder
    )

    # Assert for SERVICE_FINDER source
    assert result_service_finder.source == ClinicalCodeSource.SERVICE_FINDER
