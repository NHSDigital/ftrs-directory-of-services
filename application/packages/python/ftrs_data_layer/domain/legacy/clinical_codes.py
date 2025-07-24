from ftrs_data_layer.domain.legacy.base import LegacyDoSModel
from sqlmodel import Field, Relationship


class SymptomGroup(LegacyDoSModel, table=True):
    __tablename__ = "symptomgroups"

    id: int = Field(primary_key=True)
    name: str
    zcodeexists: bool | None


class SymptomDiscriminator(LegacyDoSModel, table=True):
    __tablename__ = "symptomdiscriminators"

    id: int = Field(primary_key=True)
    description: str | None
    synonyms: list["SymptomDiscriminatorSynonym"] = Relationship()


class SymptomDiscriminatorSynonym(LegacyDoSModel, table=True):
    __tablename__ = "symptomdiscriminatorsynonyms"

    id: int = Field(primary_key=True)
    name: str | None
    symptomdiscriminatorid: int = Field(foreign_key="symptomdiscriminators.id")


class SymptomGroupSymptomDiscriminator(LegacyDoSModel, table=True):
    __tablename__ = "symptomgroupsymptomdiscriminators"

    id: int = Field(primary_key=True)
    symptomgroupid: int = Field(foreign_key="symptomgroups.id")
    symptomdiscriminatorid: int = Field(foreign_key="symptomdiscriminators.id")

    symptomgroup: SymptomGroup = Relationship()
    symptomdiscriminator: SymptomDiscriminator = Relationship()


class Disposition(LegacyDoSModel, table=True):
    __tablename__ = "dispositions"

    id: int = Field(primary_key=True)
    name: str
    dxcode: str | None
    dispositiontime: int | None
