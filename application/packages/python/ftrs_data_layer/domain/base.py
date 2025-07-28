from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DBModel(BaseModel):
    """
    Base model for all database models.
    """

    id: UUID = Field(default_factory=uuid4)
    createdBy: str | None = "SYSTEM"
    createdDateTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
    modifiedBy: str | None = "SYSTEM"
    modifiedDateTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
