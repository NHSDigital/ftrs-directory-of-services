# services/crud-apis/healthcare_service/tests/test_validators.py
from typing import NoReturn

import pytest
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)
from pydantic import ValidationError

from healthcare_service.app.services.validators import (
    HealthcareServiceCreatePayloadValidator,
)


def test_validate_with_valid() -> NoReturn:
    payload = {
        "name": "Healthcare Service",
        "type": HealthcareServiceType.GP_CONSULTATION_SERVICE,
        "category": HealthcareServiceCategory.GP_SERVICES,
        "createdBy": "AdminUser",
        "active": True,
    }
    validator = HealthcareServiceCreatePayloadValidator(**payload)
    assert validator.name == "Healthcare Service"


def test_validate_with_empty_name() -> NoReturn:
    payload = {
        "name": "   ",
        "type": HealthcareServiceType.GP_CONSULTATION_SERVICE,
        "category": HealthcareServiceCategory.GP_SERVICES,
        "createdBy": "AdminUser",
        "active": True,
    }
    with pytest.raises(ValidationError) as exc_info:
        HealthcareServiceCreatePayloadValidator(**payload)
    assert str(exc_info.value).__contains__(
        "1 validation error for HealthcareServiceCreatePayloadValidator\nname\n"
    )


def test_validate_with_invalid_type() -> NoReturn:
    payload = {
        "name": "Healthcare Service",
        "type": "InvalidType",
        "category": HealthcareServiceCategory.GP_SERVICES,
        "createdBy": "AdminUser",
        "active": True,
    }
    with pytest.raises(ValidationError) as exc_info:
        HealthcareServiceCreatePayloadValidator(**payload)
    assert str(exc_info.value).__contains__(
        "1 validation error for HealthcareServiceCreatePayloadValidator\ntype\n"
    )


def test_validate_with_invalid_category() -> NoReturn:
    payload = {
        "name": "Healthcare Service",
        "type": HealthcareServiceType.GP_CONSULTATION_SERVICE,
        "category": "InvalidCategory",
        "createdBy": "AdminUser",
        "active": True,
    }
    with pytest.raises(ValidationError) as exc_info:
        HealthcareServiceCreatePayloadValidator(**payload)
    assert str(exc_info.value).__contains__(
        "1 validation error for HealthcareServiceCreatePayloadValidator\ncategory\n"
    )


def test_validate_with_invalid_created_by() -> NoReturn:
    payload = {
        "name": "Healthcare Service",
        "type": HealthcareServiceType.GP_CONSULTATION_SERVICE,
        "category": HealthcareServiceCategory.GP_SERVICES,
        "createdBy": "   ",
        "active": True,
    }
    with pytest.raises(ValidationError) as exc_info:
        HealthcareServiceCreatePayloadValidator(**payload)
    assert str(exc_info.value).__contains__(
        "1 validation error for HealthcareServiceCreatePayloadValidator\ncreatedBy\n"
    )


def test_validate_with_missing_fields() -> NoReturn:
    payload = {
        "name": "Healthcare Service",
        "type": HealthcareServiceType.GP_CONSULTATION_SERVICE,
        # Missing category
        "createdBy": "AdminUser",
        "active": True,
    }
    with pytest.raises(ValidationError) as exc_info:
        HealthcareServiceCreatePayloadValidator(**payload)
    assert str(exc_info.value).__contains__(
        "1 validation error for HealthcareServiceCreatePayloadValidator\ncategory\n"
    )
