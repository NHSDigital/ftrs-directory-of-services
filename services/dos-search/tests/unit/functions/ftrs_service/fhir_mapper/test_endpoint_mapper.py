from uuid import UUID

import pytest
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.endpoint import Endpoint as FhirEndpoint
from ftrs_data_layer.domain.enums import (
    EndpointBusinessScenario,
    EndpointConnectionType,
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
        ("order", "is_compression_enabled", "business_scenario", "expected_count"),
        [
            (1, True, EndpointBusinessScenario.COPY, 3),
            (None, True, EndpointBusinessScenario.COPY, 2),
            (1, None, EndpointBusinessScenario.COPY, 2),
        ],
    )
    def test_create_extensions(
        self,
        endpoint_mapper,
        order,
        is_compression_enabled,
        business_scenario,
        expected_count,
        mocker,
    ):
        # Arrange
        mock_endpoint = mocker.MagicMock()
        mock_endpoint.order = order
        mock_endpoint.isCompressionEnabled = is_compression_enabled
        mock_endpoint.businessScenario = business_scenario

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
        if business_scenario is not None:
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

    def test_create_business_scenario_extension_logs_error_for_unknown(
        self, endpoint_mapper, mocker
    ):
        # Arrange
        mock_logger = mocker.patch(
            "functions.ftrs_service.fhir_mapper.endpoint_mapper.logger"
        )

        # Act
        result = endpoint_mapper._create_business_scenario_extension("UnknownScenario")

        # Assert
        assert result is None
        mock_logger.error.assert_called_once_with(
            "Unknown business scenario: UnknownScenario"
        )

    def test_create_extensions_with_compression_false(
        self, endpoint_mapper, create_endpoint
    ):
        # Arrange - Test with is_compression_enabled=False (not None)
        endpoint = create_endpoint(is_compression_enabled=False)

        # Act
        extensions = endpoint_mapper._create_extensions(endpoint)

        # Assert
        # Should have order and business scenario but compression should be False
        assert any(ext.get("valueBoolean") is False for ext in extensions)

    def test_create_connection_type_lowercase(self, endpoint_mapper, create_endpoint):
        # Arrange - Test that connection type is properly lowercased
        endpoint = create_endpoint(connection_type=EndpointConnectionType.ITK)

        # Act
        result = endpoint_mapper._create_connection_type(endpoint)

        # Assert
        assert result.code == "itk"

    def test_create_connection_type_http(self, endpoint_mapper, create_endpoint):
        # Arrange
        endpoint = create_endpoint(connection_type="http")

        # Act
        result = endpoint_mapper._create_connection_type(endpoint)

        # Assert
        assert result.code == "http"
        assert (
            result.system
            == "https://fhir.nhs.uk/England/CodeSystem/England-EndpointConnection"
        )

    def test_create_payload_mime_type(self, endpoint_mapper, create_endpoint):
        # Arrange
        endpoint = create_endpoint()

        # Act
        result = endpoint_mapper._create_payload_mime_type(endpoint)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == endpoint.payloadMimeType.value

    def test_create_extensions_includes_all_fields(
        self, endpoint_mapper, create_endpoint
    ):
        # Arrange - Endpoint with all extension fields
        endpoint = create_endpoint(
            order=1,
            is_compression_enabled=True,
            business_scenario=EndpointBusinessScenario.PRIMARY,
        )

        # Act
        extensions = endpoint_mapper._create_extensions(endpoint)

        # Assert - Should have order, compression, and business scenario
        assert len(extensions) == 3
        assert any(ext.get("valueInteger") == 1 for ext in extensions)
        assert any(ext.get("valueBoolean") is True for ext in extensions)
        assert any(ext.get("valueCode") == "primary-recipient" for ext in extensions)

    def test_create_managing_organization_with_different_id(
        self, endpoint_mapper, create_endpoint
    ):
        # Arrange
        custom_org_id = UUID("99999999999999999999999999999999")
        endpoint = create_endpoint(managed_by_organisation=custom_org_id)

        # Act
        result = endpoint_mapper._create_managing_organization(endpoint)

        # Assert
        assert result["reference"] == f"Organization/{custom_org_id}"

    def test_create_fhir_endpoint_all_fields(self, endpoint_mapper, create_endpoint):
        # Arrange - Create endpoint with all fields populated
        endpoint_id = UUID("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        endpoint = create_endpoint(
            endpoint_id=endpoint_id,
            order=1,
            is_compression_enabled=True,
            business_scenario=EndpointBusinessScenario.PRIMARY,
            connection_type="email",
        )

        # Act
        fhir_endpoint = endpoint_mapper._create_fhir_endpoint(endpoint)

        # Assert
        assert fhir_endpoint.id == str(endpoint_id)
        assert len(fhir_endpoint.extension) == 3
        assert fhir_endpoint.connectionType.code == "email"

    def test_business_scenario_map_contains_expected_values(self, endpoint_mapper):
        # Assert the mapper contains the expected business scenario mappings
        assert endpoint_mapper.BUSINESS_SCENARIO_MAP["Primary"] == "primary-recipient"
        assert endpoint_mapper.BUSINESS_SCENARIO_MAP["Copy"] == "copy-recipient"
        assert len(endpoint_mapper.BUSINESS_SCENARIO_MAP) == 2
