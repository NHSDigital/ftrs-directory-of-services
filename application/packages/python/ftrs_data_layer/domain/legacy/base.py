from sqlmodel import MetaData, SQLModel


# TODO: FDOS-383 - note, schema for tables is already here
class LegacyDoSModel(SQLModel):
    metadata = MetaData(schema="pathwaysdos")
