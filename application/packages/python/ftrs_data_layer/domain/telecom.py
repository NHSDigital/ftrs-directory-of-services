from typing_extensions import Self, Annotated, Union
from ftrs_data_layer.domain.enums import TelecomType
from pydantic import BaseModel, Field, model_validator, HttpUrl
from email_validator import validate_email
from pydantic_extra_types.phone_numbers import PhoneNumberValidator


class Telecom(BaseModel):
    type: TelecomType = Field(frozen=True)
    value: str
    isPublic: bool

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
            PhoneNumberValidator._parse(
                region="GB",
                number_format="NATIONAL",
                supported_regions=["GB"],
                phone_number=self.value,
            )
        return self
