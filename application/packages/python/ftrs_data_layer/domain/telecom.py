import re

from email_validator import validate_email
from ftrs_data_layer.domain.enums import TelecomType
from pydantic import BaseModel, Field, HttpUrl, model_validator
from pydantic_extra_types.phone_numbers import PhoneNumberValidator
from typing_extensions import Self


class Telecom(BaseModel):
    type: TelecomType = Field(frozen=True)
    value: str
    isPublic: bool

    def __str__(self) -> str:
        return f"Telecom(type={self.type.value},value={self.value},isPublic={self.isPublic})"

    @model_validator(mode="after")
    def check_valid_email(self) -> Self:
        if self.type == TelecomType.EMAIL:
            validate_email(self.value)
        return self

    @model_validator(mode="after")
    def check_valid_web(self) -> Self:
        if self.type == TelecomType.WEB:
            HttpUrl(url=self.value)
        return self

    @model_validator(mode="after")
    def check_valid_phone(self) -> Self:
        if self.type == TelecomType.PHONE:
            if not (re.match(r"^[\d\+\(\) ]+$", self.value)):
                msg = "invalid characters in phone number"
                raise ValueError(msg)
            PhoneNumberValidator._parse(
                region="GB",
                number_format="NATIONAL",
                supported_regions=["GB"],
                phone_number=self.value,
            )
        return self
