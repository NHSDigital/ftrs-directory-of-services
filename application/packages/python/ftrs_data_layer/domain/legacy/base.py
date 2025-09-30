from sqlmodel import MetaData, SQLModel


class LegacyDoSModel(SQLModel):
    metadata = MetaData(schema="pathwaysdos")
