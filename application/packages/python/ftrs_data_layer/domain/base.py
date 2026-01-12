from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DBModel(BaseModel):
    """
    Base model for all database models.
    """

    id: UUID = Field(default_factory=uuid4)
    createdDateTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
    modifiedDateTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
