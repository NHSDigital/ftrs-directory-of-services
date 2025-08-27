import re

from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)
from pydantic import field_validator

from healthcare_service.app.models.healthcare_service import (
    HealthcareServiceCreatePayload,
)

NAME_EMPTY_ERROR = "Healthcare service name cannot be empty."
NAME_CONTAINS_INVALID_CHARACTERS_ERROR = (
    "Healthcare service name contains invalid characters."
)
TYPE_EMPTY_ERROR = "Healthcare service type cannot be empty."
TYPE_MISMATCH_ERROR = "Healthcare service type must be one of the following: "
CATEGORY_EMPTY_ERROR = "Healthcare service category cannot be empty."
CATEGORY_MISMATCH_ERROR = "Healthcare service category must be one of the following: "
CREATED_BY_EMPTY_ERROR = "createdBy cannot be empty."


class HealthcareServiceCreatePayloadValidator(HealthcareServiceCreatePayload):
    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Validates the name field to ensure it is not empty or whitespace and doesnt have special characters."""
        if not v.strip():
            raise ValueError(NAME_EMPTY_ERROR)
        if not re.match(r"^[a-zA-Z0-9_\- ]+$", v.strip()):
            raise ValueError(NAME_CONTAINS_INVALID_CHARACTERS_ERROR)
        return v

    @field_validator("type")
    def validate_type(cls, v: str) -> str:
        """Validates the type field to ensure it is not empty or whitespace."""
        if not v.strip():
            raise ValueError(TYPE_EMPTY_ERROR)
        valid_types = [type.value for type in HealthcareServiceType]
        if v not in valid_types:
            raise ValueError(TYPE_MISMATCH_ERROR + f"{', '.join(valid_types)}")
        return v

    @field_validator("category")
    def validate_category(cls, v: str) -> str:
        """Validates the category field to ensure it is not empty or whitespace."""
        if not v.strip():
            raise ValueError(CATEGORY_EMPTY_ERROR)
        # Get list of valid values from enum
        valid_categories = [category.value for category in HealthcareServiceCategory]
        if v not in valid_categories:
            raise ValueError(CATEGORY_MISMATCH_ERROR + f"{', '.join(valid_categories)}")
        return v

    @field_validator("createdBy")
    def validate_created_by(cls, v: str) -> str:
        """Validates the createdBy field to ensure it is not empty or whitespace."""
        if not v.strip():
            raise ValueError(CREATED_BY_EMPTY_ERROR)
        return v
