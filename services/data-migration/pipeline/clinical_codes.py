from enum import Enum
from typing import Annotated, List, Literal

import pandas as pd
from ftrs_data_layer.repository.dynamodb.document_level import DocumentLevelRepository
from pydantic import BaseModel
from typer import Option

from pipeline.utils.dos_db import get_clinical_codes


class CodeType(str, Enum):
    SYMPTOM_GROUP = "Symptom Group (SG)"
    SYMPTOM_DISCRIMINATOR = "Symptom Discriminator (SD)"
    DISPOSITION = "Disposition (Dx)"


class SGSDCombination(BaseModel):
    id: str
    value: str


class ClinicalCode(BaseModel):
    id: str
    field: str = "item"
    source: str  # TODO @marksp: enumerate this field to enforce set values
    codeID: str | int  # maybe int depending on type
    codeType: CodeType
    codeValue: str


class SymptomGroup(ClinicalCode):
    codeID: int
    codeType: Literal[CodeType.SYMPTOM_GROUP] = CodeType.SYMPTOM_GROUP
    zcodeexists: bool = False
    combinations: List[SGSDCombination] | None

    @classmethod
    def from_dos(cls, data: dict) -> "SymptomGroup":
        if data["combinations"] is not None:
            combinations = [
                SGSDCombination(id=item.split("\\")[0], value=item.split("\\")[1])
                for item in [item for item in data["combinations"].split(";")]
            ]
        else:
            combinations = None

        return SymptomGroup(
            id=data["id"],
            field=data["field"],
            source=data["source"],
            codeID=data["codeid"],
            codeType=CodeType.SYMPTOM_GROUP,
            codeValue=data["codevalue"],
            zcodeexists=data["zcodeexists"],
            combinations=combinations,
        )

    @property
    def indexes(self) -> dict:
        """
        Return the indexes for the Organisation model.
        """
        return {}


class SymptomDiscriminator(ClinicalCode):
    codeID: int
    codeType: Literal[CodeType.SYMPTOM_DISCRIMINATOR] = CodeType.SYMPTOM_DISCRIMINATOR
    synonyms: List[str] | None
    combinations: List[SGSDCombination] | None

    @classmethod
    def from_dos(cls, data: dict) -> "SymptomDiscriminator":
        if data["synonyms"] is not None:
            synonyms = data["synonyms"].split(";")
        else:
            synonyms = None

        if data["combinations"] is not None:
            combinations = [
                SGSDCombination(id=item.split("\\")[0], value=item.split("\\")[1])
                for item in [item for item in data["combinations"].split(";")]
            ]
        else:
            combinations = None

        return SymptomDiscriminator(
            id=data["id"],
            field=data["field"],
            source=data["source"],
            codeID=data["codeid"],
            codeType=CodeType.SYMPTOM_DISCRIMINATOR,
            codeValue=data["codevalue"],
            synonyms=synonyms,
            combinations=combinations,
        )

    @property
    def indexes(self) -> dict:
        """
        Return the indexes for the Organisation model.
        """
        return {}


class Disposition(ClinicalCode):
    codeID: str
    codeType: Literal[CodeType.DISPOSITION] = CodeType.DISPOSITION
    time: int

    @classmethod
    def from_dos(cls, data: dict) -> "Disposition":
        return Disposition(
            id=data["id"],
            field=data["field"],
            source=data["source"],
            codeID=data["codeid"],
            codeType=CodeType.DISPOSITION,
            codeValue=data["codevalue"],
            time=data["time"],
        )

    @property
    def indexes(self) -> dict:
        """
        Return the indexes for the Organisation model.
        """
        return {}


def model_clinical_codes(df: pd.DataFrame) -> list:
    df = df.replace({pd.NA: None})

    clinical_codes = []
    for _, row in df.iterrows():
        if row["codetype"] == CodeType.DISPOSITION:
            clinical_codes.append(Disposition.from_dos(row))
        elif row["codetype"] == CodeType.SYMPTOM_DISCRIMINATOR:
            clinical_codes.append(SymptomDiscriminator.from_dos(row))
        elif row["codetype"] == CodeType.SYMPTOM_GROUP:
            clinical_codes.append(SymptomGroup.from_dos(row))
        else:
            print("bad codeType")

    return clinical_codes


def write_clinical_codes(ddb_uri: str, modelled_codes: list) -> None:
    repository = DocumentLevelRepository["clinical_code"](
        table_name="test_clinical_codes",
        model_cls=ClinicalCode,
        endpoint_url=ddb_uri,
    )

    for item in modelled_codes:
        if type(item) is Disposition:
            disp = Disposition.model_validate(item)
            repository.insert(disp)
        elif type(item) is SymptomDiscriminator:
            sd = SymptomDiscriminator.model_validate(item)
            repository.insert(sd)
        elif type(item) is SymptomGroup:
            sg = SymptomGroup.model_validate(item)
            repository.insert(sg)


def refresh_clinical_codes(
    db_uri: Annotated[str, Option(..., help="URI to connect to the source database")],
    ddb_uri: Annotated[str, Option(..., help="URI to connect to the target database")],
) -> None:
    """
    Extract GP practice data from the source database and save it to the specified path.
    """
    postgres_codes = get_clinical_codes(db_uri)

    modelled_codes = model_clinical_codes(postgres_codes)

    # deleted_codes = find_codes_to_delete(ddb_uri, modelled_codes)

    write_clinical_codes(ddb_uri, modelled_codes)


refresh_clinical_codes(
    "postgresql://postgres:postgres@localhost:5432/postgres", "http://localhost:8000"
)
