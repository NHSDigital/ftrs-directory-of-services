from datetime import datetime, time
from typing import Annotated, Literal

from ftrs_data_layer.domain.enums import DayOfWeek, OpeningTimeCategory
from pydantic import BaseModel, Field


class AvailableTime(BaseModel):
    category: Literal[OpeningTimeCategory.AVAILABLE_TIME] = (
        OpeningTimeCategory.AVAILABLE_TIME
    )
    dayOfWeek: DayOfWeek
    startTime: time
    endTime: time
    allDay: bool = False


class AvailableTimeVariation(BaseModel):
    category: Literal[OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS] = (
        OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS
    )
    description: str | None = None
    startTime: datetime
    endTime: datetime


class AvailableTimePublicHolidays(BaseModel):
    category: Literal[OpeningTimeCategory.AVAILABLE_TIME_PUBLIC_HOLIDAYS] = (
        OpeningTimeCategory.AVAILABLE_TIME_PUBLIC_HOLIDAYS
    )
    startTime: time
    endTime: time


class NotAvailable(BaseModel):
    category: Literal[OpeningTimeCategory.NOT_AVAILABLE] = (
        OpeningTimeCategory.NOT_AVAILABLE
    )
    description: str | None = None
    startTime: datetime
    endTime: datetime


OpeningTime = Annotated[
    AvailableTime | AvailableTimeVariation | AvailableTimePublicHolidays | NotAvailable,
    Field(discriminator="category"),
]
