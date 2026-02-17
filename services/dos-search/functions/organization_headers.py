from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VERSION_VALUE = "1"


class InvalidVersionError(ValueError):
    """Raised when header version is invalid"""

    def __init__(self) -> None:
        super().__init__(
            f"Invalid version found in supplied headers: version must be '{VERSION_VALUE}'"
        )


class OrganizationHeaders(BaseModel):
    authorization: str = Field(alias="authorization")
    version: str = Field(alias="version")
    nhsd_request_id: str = Field(alias="nhsd-request-id")

    content_type: str | None = Field(default=None, alias="content-type")
    nhsd_correlation_id: str | None = Field(default=None, alias="nhsd-correlation-id")
    x_correlation_id: str | None = Field(default=None, alias="x-correlation-id")
    x_request_id: str | None = Field(default=None, alias="x-request-id")
    end_user_role: str | None = Field(default=None, alias="end-user-role")
    application_id: str | None = Field(default=None, alias="application-id")
    application_name: str | None = Field(default=None, alias="application-name")
    request_start_time: str | None = Field(default=None, alias="request-start-time")
    accept: str | None = Field(default=None, alias="accept")
    accept_encoding: str | None = Field(default=None, alias="accept-encoding")
    accept_language: str | None = Field(default=None, alias="accept-language")
    user_agent: str | None = Field(default=None, alias="user-agent")
    host: str | None = Field(default=None, alias="host")
    x_amzn_trace_id: str | None = Field(default=None, alias="x-amzn-trace-id")
    x_forwarded_for: str | None = Field(default=None, alias="x-forwarded-for")
    x_forwarded_port: str | None = Field(default=None, alias="x-forwarded-port")
    x_forwarded_proto: str | None = Field(default=None, alias="x-forwarded-proto")

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:  # noqa: ANN401
        if isinstance(data, dict):
            return {k.lower(): v for k, v in data.items()}
        return data

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if v != VERSION_VALUE:
            raise InvalidVersionError
        return v

    @classmethod
    def get_allowed_headers(cls) -> list[str]:
        """Get allowed headers from OrganizationHeaders model."""
        return sorted(
            field_info.alias
            for field_info in cls.model_fields.values()
            if field_info.alias
        )
