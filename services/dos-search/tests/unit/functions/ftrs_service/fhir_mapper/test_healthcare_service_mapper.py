from uuid import uuid4

import pytest
from fhir.resources.R4B.healthcareservice import (
    HealthcareService as FhirHealthcareService,
)
from ftrs_data_layer.domain import HealthcareService, HealthcareServiceTelecom
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)

from functions.ftrs_service.fhir_mapper.healthcare_service_mapper import (
    HealthcareServiceMapper,
)


@pytest.fixture
def healthcare_service_mapper() -> HealthcareServiceMapper:
    return HealthcareServiceMapper()


@pytest.fixture
def mock_healthcare_service() -> HealthcareService:
    return HealthcareService(
        id=uuid4(),
        identifier_oldDoS_uid="123456",
        active=True,
        category=HealthcareServiceCategory.GP_SERVICES,
        type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
        providedBy=uuid4(),
        location=uuid4(),
        name="Test Healthcare Service",
        telecom=HealthcareServiceTelecom(
            phone_public="01234567890",
            phone_private=None,
            email="test@example.com",
            web="https://example.com",
        ),
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
    )


@pytest.fixture
def mock_healthcare_service_minimal() -> HealthcareService:
    return HealthcareService(
        id=uuid4(),
        identifier_oldDoS_uid=None,
        active=True,
        category=HealthcareServiceCategory.GP_SERVICES,
        type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
        providedBy=None,
        location=None,
        name="Minimal Healthcare Service",
        telecom=None,
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
    )


class TestHealthcareServiceMapper:
    def test_map_to_fhir_healthcare_service_success(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        assert isinstance(result, FhirHealthcareService)
        assert result.id == str(mock_healthcare_service.id)

    def test_map_to_fhir_healthcare_service_identifiers(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        assert len(result.identifier) == 1
        assert result.identifier[0].use == "official"
        assert result.identifier[0].system == "https://fhir.nhs.uk/Id/dos-service-id"
        assert result.identifier[0].value == "123456"

    def test_map_to_fhir_healthcare_service_no_identifier(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service_minimal: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service_minimal
        )

        assert result.identifier == []

    def test_map_to_fhir_healthcare_service_provided_by(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        assert (
            result.providedBy.reference
            == f"Organization/{mock_healthcare_service.providedBy}"
        )

    def test_map_to_fhir_healthcare_service_no_provided_by(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service_minimal: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service_minimal
        )

        assert result.providedBy is None

    def test_map_to_fhir_healthcare_service_location(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        assert len(result.location) == 1
        assert (
            result.location[0].reference
            == f"Location/{mock_healthcare_service.location}"
        )

    def test_map_to_fhir_healthcare_service_no_location(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service_minimal: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service_minimal
        )

        assert result.location == []

    def test_map_to_fhir_healthcare_service_type(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        assert len(result.type) == 1
        assert result.type[0].coding[0].code == "GP Consultation Service"
        assert (
            result.type[0].coding[0].system
            == "http://hl7.org/fhir/ValueSet/service-type"
        )

    def test_map_to_fhir_healthcare_service_no_type(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
    ) -> None:
        service = HealthcareService.model_construct(
            id=uuid4(),
            identifier_oldDoS_uid=None,
            active=True,
            category=None,
            type=None,
            providedBy=None,
            location=None,
            name="No Type Service",
            telecom=None,
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
        )

        result = healthcare_service_mapper.map_to_fhir_healthcare_service(service)

        assert result.type == []

    def test_map_to_fhir_healthcare_service_telecom_all_fields(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

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
        mock_healthcare_service_minimal: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service_minimal
        )

        assert result.telecom == []

    def test_map_to_fhir_healthcare_service_partial_telecom(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: HealthcareService,
    ) -> None:
        service = mock_healthcare_service.model_copy(
            update={
                "telecom": HealthcareServiceTelecom(
                    phone_public="01234567890",
                    phone_private=None,
                    email=None,
                    web=None,
                )
            }
        )

        result = healthcare_service_mapper.map_to_fhir_healthcare_service(service)

        assert len(result.telecom) == 1
        assert result.telecom[0].system == "phone"

    def test_map_to_fhir_healthcare_service_telecom_with_private_phone(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: HealthcareService,
    ) -> None:
        service = mock_healthcare_service.model_copy(
            update={
                "telecom": HealthcareServiceTelecom(
                    phone_public="01234567890",
                    phone_private="09876543210",
                    email="test@example.com",
                    web="https://example.com",
                )
            }
        )

        result = healthcare_service_mapper.map_to_fhir_healthcare_service(service)

        assert len(result.telecom) == 4
        phones = [t for t in result.telecom if t.system == "phone"]
        assert len(phones) == 2

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
        mock_healthcare_service: HealthcareService,
    ) -> None:
        service = mock_healthcare_service.model_copy(
            update={
                "telecom": HealthcareServiceTelecom(
                    phone_public=None,
                    phone_private="09876543210",
                    email=None,
                    web=None,
                )
            }
        )

        result = healthcare_service_mapper.map_to_fhir_healthcare_service(service)

        assert len(result.telecom) == 1
        assert result.telecom[0].system == "phone"
        assert result.telecom[0].value == "09876543210"
        assert result.telecom[0].extension[0].valueString == "Clinician Access Only"

    def test_map_to_fhir_healthcare_service_type_display(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
        mock_healthcare_service: HealthcareService,
    ) -> None:
        result = healthcare_service_mapper.map_to_fhir_healthcare_service(
            mock_healthcare_service
        )

        assert result.type[0].coding[0].display == "GP Consultation Service"

    def test_map_to_fhir_healthcare_service_type_without_value_attribute(
        self,
        healthcare_service_mapper: HealthcareServiceMapper,
    ) -> None:
        service = HealthcareService.model_construct(
            id=uuid4(),
            identifier_oldDoS_uid=None,
            active=True,
            category=HealthcareServiceCategory.GP_SERVICES,
            type="GP Consultation Service",
            providedBy=None,
            location=None,
            name="String Type Service",
            telecom=None,
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
        )

        result = healthcare_service_mapper.map_to_fhir_healthcare_service(service)

        assert len(result.type) == 1
        assert result.type[0].coding[0].code == "GP Consultation Service"
        assert result.type[0].coding[0].display == "GP Consultation Service"
