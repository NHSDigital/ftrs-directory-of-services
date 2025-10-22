from uuid import UUID

import pytest
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.endpoint import Endpoint as FhirEndpoint
from ftrs_data_layer.domain.enums import (
    EndpointDescription,
    EndpointPayloadType,
)

from functions.ftrs_service.fhir_mapper.endpoint_mapper import EndpointMapper


@pytest.fixture
def endpoint_mapper():
    return EndpointMapper()


class TestEndpointMapper:
    def test_create_payload_type(self, endpoint_mapper, endpoint):
        # Act
        result = endpoint_mapper._create_payload_type(endpoint)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], CodeableConcept)
        assert len(result[0].coding) == 1
        assert (
            result[0].coding[0].system
            == "http://hl7.org/fhir/ValueSet/endpoint-payload-type"
        )
        assert result[0].coding[0].code == EndpointPayloadType.ED.value

    def test_create_endpoint(self, endpoint_mapper, endpoint):
        endpoint = endpoint_mapper._create_fhir_endpoint(endpoint)

        # Assert
        assert isinstance(endpoint, FhirEndpoint)
        assert endpoint.id == "12345678-1234-5678-1234-567812345678"  # gitleaks:allow
        assert endpoint.status == "active"
        assert endpoint.connectionType.code == "itk"
        assert endpoint.address == "https://example.com/endpoint"
        assert len(endpoint.payloadType) == 1
        assert (
            endpoint.payloadType[0].coding[0].code
            == "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0"
        )
        assert endpoint.payloadMimeType == ["application/fhir"]
        assert len(endpoint.extension) == 3

    def test_create_endpoint_with_unsupported_connection_type(
        self, endpoint_mapper, create_endpoint
    ):
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Input should be 'itk', 'email', 'telno' or 'http'"
        ):
            create_endpoint(connection_type="unsupported")

    def test_create_address(self, endpoint_mapper, create_endpoint):
        # Arrange
        address = "https://test-address.org/fhir"
        endpoint = create_endpoint(address=address)

        # Act
        result = endpoint_mapper._create_address(endpoint)

        # Assert
        assert result == address

    def test_create_managing_organization(self, endpoint_mapper, create_endpoint):
        # Arrange
        org_id = UUID("12345678123456781234567812345678")
        endpoint = create_endpoint(managed_by_organisation=org_id)

        # Act
        result = endpoint_mapper._create_managing_organization(endpoint)

        # Assert
        assert result == {"reference": f"Organization/{org_id}"}

    def test_create_order_extension(self, endpoint_mapper):
        # Act
        result = endpoint_mapper._create_order_extension(1)

        # Assert
        assert result == {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganizationEndpointOrder",
            "valueInteger": 1,
        }

    def test_create_compression_extension(self, endpoint_mapper):
        # Act
        result = endpoint_mapper._create_compression_extension(True)

        # Assert
        assert result == {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointCompression",
            "valueBoolean": True,
        }

    @pytest.mark.parametrize(
        ("business_scenario", "expected_result"),
        [
            (
                "Primary",
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointBusinessScenario",
                    "valueCode": "primary-recipient",
                },
            ),
            (
                "Copy",
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointBusinessScenario",
                    "valueCode": "copy-recipient",
                },
            ),
            ("Unknown", None),
            ("", None),
            (None, None),
        ],
    )
    def test_create_business_scenario_extension(
        self, endpoint_mapper, business_scenario, expected_result
    ):
        # Act
        result = endpoint_mapper._create_business_scenario_extension(business_scenario)

        # Assert
        assert result == expected_result

    @pytest.mark.parametrize(
        ("order", "is_compression_enabled", "description", "expected_count"),
        [
            (1, True, EndpointDescription.COPY, 3),
            (None, True, EndpointDescription.COPY, 2),
            (1, None, EndpointDescription.COPY, 2),
        ],
    )
    def test_create_extensions(
        self,
        endpoint_mapper,
        order,
        is_compression_enabled,
        description,
        expected_count,
        mocker,
    ):
        # Arrange
        mock_endpoint = mocker.MagicMock()
        mock_endpoint.order = order
        mock_endpoint.isCompressionEnabled = is_compression_enabled
        mock_endpoint.description = description

        # Act
        extensions = endpoint_mapper._create_extensions(mock_endpoint)

        # Assert
        assert len(extensions) == expected_count
        if order is not None:
            assert any(
                ext["url"].endswith("OrganizationEndpointOrder") for ext in extensions
            )
        if is_compression_enabled is not None:
            assert any(ext["url"].endswith("EndpointCompression") for ext in extensions)
        if description is not None:
            assert any(
                ext["url"].endswith("EndpointBusinessScenario") for ext in extensions
            )

    def test_map_to_endpoints_empty_list(self, endpoint_mapper, create_organisation):
        # Arrange
        org_value = create_organisation(endpoints=[])

        # Act
        endpoints = endpoint_mapper.map_to_fhir_endpoints(org_value)

        # Assert
        assert endpoints == []

    def test_map_to_endpoints_multiple_endpoints(
        self,
        endpoint_mapper,
        create_organisation,
        create_endpoint,
    ):
        # Arrange
        endpoint1 = create_endpoint(
            endpoint_id=UUID("11111111111111111111111111111111"), connection_type="itk"
        )
        endpoint2 = create_endpoint(
            endpoint_id=UUID("22222222222222222222222222222222"),
            connection_type="email",
        )
        endpoint3 = create_endpoint(
            endpoint_id=UUID("33333333333333333333333333333333"),
            connection_type="telno",
        )

        org_value = create_organisation(endpoints=[endpoint1, endpoint2, endpoint3])

        # Act
        endpoints = endpoint_mapper.map_to_fhir_endpoints(org_value)

        # Assert
        assert len(endpoints) == 3
        assert (
            endpoints[0].id == "11111111-1111-1111-1111-111111111111"  # gitleaks:allow
        )
        assert endpoints[0].connectionType.code == "itk"
        assert (
            endpoints[1].id == "22222222-2222-2222-2222-222222222222"  # gitleaks:allow
        )
        assert endpoints[1].connectionType.code == "email"
        assert (
            endpoints[2].id == "33333333-3333-3333-3333-333333333333"  # gitleaks:allow
        )
        assert endpoints[2].connectionType.code == "telno"
