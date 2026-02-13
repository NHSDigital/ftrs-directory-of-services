from unittest.mock import MagicMock

import pytest
from fhir.resources.R4B.healthcareservice import (
    HealthcareService as FhirHealthcareService,
)

from functions.ftrs_service.fhir_mapper.healthcare_service_mapper import (
    HealthcareServiceMapper,
)


@pytest.fixture
def healthcare_service_mapper() -> HealthcareServiceMapper:
    return HealthcareServiceMapper()


@pytest.fixture
def mock_healthcare_service() -> MagicMock:
    mock = MagicMock()
    mock.id = "service-123"
    mock.name = "Test Healthcare Service"
    mock.active = True
    mock.identifier_oldDoS_uid = "123456"
    mock.providedBy = "org-123"
    mock.location = "loc-123"

    # Mock category
    mock_category = MagicMock()
    mock_category.value = "pharmacy"
    mock.category = mock_category

    # Mock type
    mock_type = MagicMock()
    mock_type.value = "dispensing"
    mock.type = mock_type

    # Mock telecom
    mock_telecom = MagicMock()
    mock_telecom.phone_public = "01234567890"
    mock_telecom.phone_private = None  # Explicitly set to None
    mock_telecom.email = "test@example.com"
    mock_telecom.web = "https://example.com"
    mock.telecom = mock_telecom

    return mock


@pytest.fixture
def mock_healthcare_service_minimal() -> MagicMock:
    mock = MagicMock()
    mock.id = "service-123"
    mock.name = "Minimal Healthcare Service"
    mock.active = True
    mock.identifier_oldDoS_uid = None
    mock.providedBy = None
    mock.location = None
    mock.category = None
    mock.type = None
    mock.telecom = None
    return mock


class TestHealthcareServiceMapper:
    def test_map_to_fhir_healthcare_service_success(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert isinstance(result, FhirHealthcareService)
        assert result.id == str(mock_healthcare_service.id)
        assert result.name == mock_healthcare_service.name

    def test_map_to_fhir_healthcare_service_identifiers(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert len(result.identifier) == 1
        assert result.identifier[0].use == "official"
        assert result.identifier[0].system == "https://fhir.nhs.uk/Id/dos-service-id"
        assert result.identifier[0].value == "123456"

    def test_map_to_fhir_healthcare_service_no_identifier(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service_minimal: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service_minimal
        )

        # Assert
        assert result.identifier == []

    def test_map_to_fhir_healthcare_service_provided_by(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert (
            result.providedBy.reference
            == f"Organization/{mock_healthcare_service.providedBy}"
        )

    def test_map_to_fhir_healthcare_service_no_provided_by(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service_minimal: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service_minimal
        )

        # Assert
        assert result.providedBy is None

    def test_map_to_fhir_healthcare_service_location(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert len(result.location) == 1
        assert (
            result.location[0].reference
            == f"Location/{mock_healthcare_service.location}"
        )

    def test_map_to_fhir_healthcare_service_no_location(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service_minimal: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service_minimal
        )

        # Assert
        assert result.location == []

    def test_map_to_fhir_healthcare_service_type(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert len(result.type) == 1
        assert result.type[0].coding[0].code == "dispensing"
        assert (
            result.type[0].coding[0].system
            == "http://hl7.org/fhir/ValueSet/service-type"
        )

    def test_map_to_fhir_healthcare_service_no_type(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service_minimal: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service_minimal
        )

        # Assert
        assert result.type == []

    def test_map_to_fhir_healthcare_service_telecom_all_fields(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert len(result.telecom) == 3
        phone = next((t for t in result.telecom if t.system == "phone"), None)
        email = next((t for t in result.telecom if t.system == "email"), None)
        url = next((t for t in result.telecom if t.system == "url"), None)

        assert phone is not None
        assert phone.value == "01234567890"
        assert phone.use == "work"

        assert email is not None
        assert email.value == "test@example.com"

        assert url is not None
        assert url.value == "https://example.com"

    def test_map_to_fhir_healthcare_service_no_telecom(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service_minimal: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service_minimal
        )

        # Assert
        assert result.telecom == []

    def test_map_to_fhir_healthcare_service_partial_telecom(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Arrange
        mock_healthcare_service.telecom.email = None
        mock_healthcare_service.telecom.web = None

        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert len(result.telecom) == 1
        assert result.telecom[0].system == "phone"

    def test_map_to_fhir_healthcare_service_telecom_with_private_phone(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Arrange
        mock_healthcare_service.telecom.phone_private = "09876543210"

        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert len(result.telecom) == 4
        phones = [t for t in result.telecom if t.system == "phone"]
        assert len(phones) == 2

        # Find public phone (has "Public" extension)
        public_phone = next(
            (
                p
                for p in phones
                if p.extension and p.extension[0].valueString == "Public"
            ),
            None,
        )
        assert public_phone is not None
        assert public_phone.value == "01234567890"

        # Find private phone (has "Clinician Access Only" extension)
        private_phone = next(
            (
                p
                for p in phones
                if p.extension and p.extension[0].valueString == "Clinician Access Only"
            ),
            None,
        )
        assert private_phone is not None
        assert private_phone.value == "09876543210"
        assert private_phone.use == "work"

    def test_map_to_fhir_healthcare_service_telecom_only_private_phone(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Arrange
        mock_healthcare_service.telecom.phone_public = None
        mock_healthcare_service.telecom.phone_private = "09876543210"
        mock_healthcare_service.telecom.email = None
        mock_healthcare_service.telecom.web = None

        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert len(result.telecom) == 1
        assert result.telecom[0].system == "phone"
        assert result.telecom[0].value == "09876543210"
        assert result.telecom[0].extension[0].valueString == "Clinician Access Only"

    def test_map_to_fhir_healthcare_service_type_display(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert result.type[0].coding[0].display == "dispensing"

    def test_map_to_fhir_healthcare_service_type_without_value_attribute(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Arrange - use a string instead of an object with .value
        mock_healthcare_service.type = "GP Consultation Service"

        # Act
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        # Assert
        assert len(result.type) == 1
        assert result.type[0].coding[0].code == "GP Consultation Service"
        assert result.type[0].coding[0].display == "GP Consultation Service"
