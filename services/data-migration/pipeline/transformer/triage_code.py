from ftrs_data_layer.domain import (
    ClinicalCodeSource,
    ClinicalCodeType,
)
from ftrs_data_layer.domain import (
    legacy as legacy_model,
)
from ftrs_data_layer.domain.triage_code import TriageCode


class TriageCodeTransformer:
    @classmethod
    def build_triage_code_from_symptom_group(
        cls, symptom_group: legacy_model.SymptomGroup
    ) -> TriageCode:
        """
        Transform the given symptom group into the new data model format.
        """
        return TriageCode(
            id="SG" + str(symptom_group.id),
            source=(
                ClinicalCodeSource.SERVICE_FINDER
                if symptom_group.zcodeexists is True
                else ClinicalCodeSource.PATHWAYS
            ),
            codeType=ClinicalCodeType.SYMPTOM_GROUP,
            codeID=symptom_group.id,
            codeValue=symptom_group.name,
            zCodeExists=symptom_group.zcodeexists,
        )

    @classmethod
    def build_triage_code_from_disposition(
        cls, disposition: legacy_model.Disposition
    ) -> TriageCode:
        """
        Transform the given disposition into the new data model format.
        """
        return TriageCode(
            id=disposition.dxcode,
            source=ClinicalCodeSource.PATHWAYS,
            codeType=ClinicalCodeType.DISPOSITION,
            codeID=disposition.dxcode,
            codeValue=disposition.name,
            time=disposition.dispositiontime or 0,
        )

    @classmethod
    def build_triage_code_from_symptom_discriminator(
        cls, symptom_discriminator: legacy_model.SymptomDiscriminator
    ) -> TriageCode:
        """
        Transform the given symptom discriminator into the new data model format.
        """
        return TriageCode(
            id="SD" + str(symptom_discriminator.id),
            source=ClinicalCodeSource.SERVICE_FINDER,
            codeType=ClinicalCodeType.SYMPTOM_DISCRIMINATOR,
            codeID=symptom_discriminator.id,
            codeValue=symptom_discriminator.description or "",
            synonyms=[synonym.name for synonym in symptom_discriminator.synonyms],
        )
