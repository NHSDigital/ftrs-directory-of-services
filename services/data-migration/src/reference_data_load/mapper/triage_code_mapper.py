from ftrs_data_layer.domain import ClinicalCodeSource, ClinicalCodeType
from ftrs_data_layer.domain.legacy import (
    Disposition,
    SymptomDiscriminator,
    SymptomGroup,
)
from ftrs_data_layer.domain.triage_code import TriageCode, TriageCodeCombination


class SymptomGroupMapper:
    def map(self, symptom_group: SymptomGroup) -> TriageCode:
        """
        Transform the given symptom group into the new data model format.
        """
        source = (
            ClinicalCodeSource.SERVICE_FINDER
            if symptom_group.zcodeexists is True
            else ClinicalCodeSource.PATHWAYS
        )

        return TriageCode(
            id="SG" + str(symptom_group.id),
            source=source,
            codeType=ClinicalCodeType.SYMPTOM_GROUP,
            codeID=symptom_group.id,
            codeValue=symptom_group.name,
            zCodeExists=symptom_group.zcodeexists,
        )


class SymptomDiscriminatorMapper:
    __SYMPTOM_DISCRIMINATOR_PATHWAYS_UPPER_LIMIT = 10999

    def map(self, symptom_discriminator: SymptomDiscriminator) -> TriageCode:
        """
        Transform the given disposition into the new data model format.
        """
        source = (
            ClinicalCodeSource.PATHWAYS
            if int(symptom_discriminator.id)
            <= self.__SYMPTOM_DISCRIMINATOR_PATHWAYS_UPPER_LIMIT
            else ClinicalCodeSource.SERVICE_FINDER
        )

        return TriageCode(
            id="SD" + str(symptom_discriminator.id),
            source=source,
            codeType=ClinicalCodeType.SYMPTOM_DISCRIMINATOR,
            codeID=symptom_discriminator.id,
            codeValue=symptom_discriminator.description or "",
            synonyms=[synonym.name for synonym in symptom_discriminator.synonyms],
        )


class DispositionMapper:
    def map(self, disposition: Disposition) -> TriageCode:
        """
        Transform the given symptom discriminator into the new data model format.
        """
        return TriageCode(
            id=disposition.dxcode,
            source=ClinicalCodeSource.PATHWAYS,
            codeType=ClinicalCodeType.DISPOSITION,
            codeID=disposition.dxcode,
            codeValue=disposition.name,
            time=disposition.dispositiontime or 0,
        )


class SGSDCombinationMapper:
    def map(
        self,
        symptom_group: SymptomGroup,
        symptom_discriminators: list[SymptomDiscriminator],
    ) -> dict:
        """
        Create a combination mapping between Symptom Group and Symptom Discriminators
        """
        source = (
            ClinicalCodeSource.SERVICE_FINDER
            if symptom_group.zcodeexists is True
            else ClinicalCodeSource.PATHWAYS
        )

        triage_code = TriageCode(
            id=f"SG{symptom_group.id}",
            field="combinations",
            combinations=[],
            source=source,
            codeType=ClinicalCodeType.SG_SD_PAIR,
        )

        for sd in symptom_discriminators:
            triage_code.combinations.append(
                TriageCodeCombination(
                    id=f"SD{sd.id}",
                    value=sd.description,
                )
            )

        return triage_code
