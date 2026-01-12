from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DBModel(BaseModel):
    """
    Base model for all database models.
    """

    id: UUID = Field(default_factory=uuid4)
    # NOTE: FTRS-1524 All of the existing createdBy, modifiedBy and related fields are removed from the base model.
    # Introduced the new keys individually onto the Organisation, Location and HealthcareService records
    # TODO: FTRS-1524 check if createdDateTime should be updated to createdTime (given the table)?
    # TODO: FTRS-1524 check if modifiedDateTime should be updated to modifiedTime (given the table)?
    # TODO: FTRS-1524 what is the difference between modifiedTime/lastUpdated and modifiedBy/lastUpdatedBy fields?
    # TODO: FTRS-1524 check if lastUpdated & lastUpdatedBy part of this ticket (given the BDD scenario but not in table)?

    # TODO: FTRS-1524 clarify meaning of below
    # "All of the existing `createdBy`, `modifiedBy` and related fields will need to be removed from the base model.
    # Introduce the new keys individually onto the Organisation, Location and HealthcareService records."
    # ^ Can this also be achieved by below, instead of individually adding to each model?
    # createdBy: AuditEvent = Field(default_factory=default_data_migration_audit_event)
    # createdTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
    # modifiedBy: AuditEvent = Field(default_factory=default_data_migration_audit_event)
    # modifiedTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
    # lastUpdated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    # lastUpdatedBy: AuditEvent = Field(default_factory=default_data_migration_audit_event)
