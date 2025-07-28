from typing import NoReturn
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ftrs_data_layer.domain import HealthcareService
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

from healthcare_service.app.services.healthcare_service_helper import (
    create_healthcare_service,
)


def test_create_healthcare_service_successful() -> NoReturn:
    mock_repository = Mock(spec=AttributeLevelRepository)
    test_service = HealthcareService(
        identifier_oldDoS_uid=None,
        active=True,
        category="GP Services",
        type="Primary Care Network Enhanced Access Service",
        providedBy=uuid4(),
        location=uuid4(),
        name="Test Healthcare Service",
        telecom=None,
        openingTime=None,
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
    )
    response = create_healthcare_service(
        healthcare_service=test_service, repository=mock_repository
    )

    assert response.id is not None
    assert isinstance(response.id, uuid4().__class__)
    assert response.name == test_service.name
    assert response.type == test_service.type
    mock_repository.create.assert_called_once_with(test_service)


def test_create_healthcare_service_invalid_healthcare_service() -> NoReturn:
    mock_repository = Mock(spec=AttributeLevelRepository)
    invalid_service = None  # Representing an invalid HealthcareService instance

    with pytest.raises(AttributeError):
        create_healthcare_service(
            healthcare_service=invalid_service, repository=mock_repository
        )


def test_create_healthcare_service_repository_error() -> NoReturn:
    mock_repository = Mock(spec=AttributeLevelRepository)
    test_service = HealthcareService(
        identifier_oldDoS_uid=None,
        active=True,
        category="GP Services",
        type="GP Consultation Service",
        providedBy=uuid4(),
        location=uuid4(),
        name="Test Healthcare Service",
        telecom=None,
        openingTime=None,
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
    )
    mock_repository.create.side_effect = Exception("Repository error")

    with pytest.raises(Exception) as exc_info:
        create_healthcare_service(
            healthcare_service=test_service, repository=mock_repository
        )

    assert str(exc_info.value) == "Repository error"
    mock_repository.create.assert_called_once_with(test_service)
