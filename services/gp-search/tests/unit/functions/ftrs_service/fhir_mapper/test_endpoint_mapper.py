import pytest
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.endpoint import Endpoint

from functions.ftrs_service.fhir_mapper.endpoint_mapper import EndpointMapper


@pytest.fixture
def endpoint_mapper():
    return EndpointMapper()


class TestEndpointMapper:
    @pytest.mark.parametrize(
        ("connection_type", "expected_code"),
        [
            ("fhir", "hl7-fhir-rest"),
            ("FHIR", "hl7-fhir-rest"),  # Test case insensitivity
            ("itk", "ihe-xcpd"),
            ("ITK", "ihe-xcpd"),  # Test case insensitivity
            ("email", "direct-project"),
            ("EMAIL", "direct-project"),  # Test case insensitivity
            ("unknown", None),  # Test unsupported type
            ("", None),  # Test empty string
        ],
    )
    def test_create_connection_type(
        self, endpoint_mapper, create_endpoint_value, connection_type, expected_code
    ):
        # Arrange
        endpoint_value = create_endpoint_value(connection_type=connection_type)

        # Act
        coding = endpoint_mapper._create_connection_type(endpoint_value)

        # Assert
        if expected_code:
            assert (
                coding.system
                == "http://terminology.hl7.org/CodeSystem/endpoint-connection-type"
            )
            assert coding.code == expected_code
        else:
            assert coding is None

    @pytest.mark.parametrize(
        ("format_value", "expected_mime_type"),
        [
            ("PDF", ["application/pdf"]),
            ("pdf", ["application/pdf"]),  # Test lowercase
            ("CDA", ["application/hl7-cda+xml"]),
            ("FHIR", ["application/fhir+json"]),
            ("unsupported", []),  # Test unsupported format
            ("", []),  # Test empty string
        ],
    )
    def test_create_payload_mime_type(
        self, endpoint_mapper, create_endpoint_value, format_value, expected_mime_type
    ):
        # Arrange
        endpoint_value = create_endpoint_value(format_type=format_value)

        # Act
        mime_type = endpoint_mapper._create_payload_mime_type(endpoint_value)

        # Assert
        assert mime_type == expected_mime_type

    @pytest.mark.parametrize(
        ("payload_type", "expected_result"),
        [
            ("document", True),
            ("", False),
            (
                None,
                False,
            ),  # This case would actually raise a validation error in real use
        ],
    )
    def test_create_payload_type(
        self,
        endpoint_mapper,
        create_endpoint_value,
        payload_type,
        expected_result,
        mocker,
    ):
        # For None payload_type, we need to mock
        if payload_type is None:
            # Create a mock endpoint with None payloadType for testing only
            mock_endpoint = mocker.MagicMock()
            mock_endpoint.payloadType = None
            result = endpoint_mapper._create_payload_type(mock_endpoint)
            assert result == []
        else:
            # Arrange
            endpoint_value = create_endpoint_value(payload_type=payload_type)

            # Act
            result = endpoint_mapper._create_payload_type(endpoint_value)

            # Assert
            if expected_result:
                assert len(result) == 1
                assert isinstance(result[0], CodeableConcept)
                assert len(result[0].coding) == 1
                assert (
                    result[0].coding[0].system
                    == "http://hl7.org/fhir/ValueSet/endpoint-payload-type"
                )
                assert result[0].coding[0].code == payload_type
            else:
                assert result == []

    def test_create_endpoint(self, endpoint_mapper, create_endpoint_value):
        # Arrange
        endpoint_value = create_endpoint_value()

        # Act
        endpoint = endpoint_mapper._create_endpoint(endpoint_value)

        # Assert
        assert isinstance(endpoint, Endpoint)
        assert endpoint.id == "endpoint-123"
        assert endpoint.status == "active"
        assert endpoint.connectionType.code == "hl7-fhir-rest"
        assert endpoint.address == "https://example.org/fhir"
        assert len(endpoint.payloadType) == 1
        assert endpoint.payloadType[0].coding[0].code == "document"
        assert endpoint.payloadMimeType == ["application/pdf"]
        assert len(endpoint.header) == 3

    def test_create_endpoint_with_unsupported_connection_type(
        self, endpoint_mapper, create_endpoint_value
    ):
        # Arrange
        endpoint_value = create_endpoint_value(connection_type="unsupported")

        # Act
        endpoint = endpoint_mapper._create_endpoint(endpoint_value)

        # Assert
        assert endpoint.connectionType is None

    def test_create_address(self, endpoint_mapper, create_endpoint_value):
        # Arrange
        address = "https://test-address.org/fhir"
        endpoint_value = create_endpoint_value(address=address)

        # Act
        result = endpoint_mapper._create_address(endpoint_value)

        # Assert
        assert result == address

    def test_create_managing_organization(self, endpoint_mapper, create_endpoint_value):
        # Arrange
        org_id = "test-org-123"
        endpoint_value = create_endpoint_value(managed_by_organisation=org_id)

        # Act
        result = endpoint_mapper._create_managing_organization(endpoint_value)

        # Assert
        assert result == {"reference": f"Organization/{org_id}"}

    def test_create_status(self, endpoint_mapper):
        # Act
        result = endpoint_mapper._create_status()

        # Assert
        assert result == "active"

    @pytest.mark.parametrize(
        ("order", "is_compression_enabled", "description", "expected_headers"),
        [
            (
                1,
                True,
                "Test",
                [
                    "header_order 1",
                    "header_is_compression_enabled True",
                    "header_business_scenario Test",
                ],
            ),
            (
                None,
                True,
                "Test",
                ["header_is_compression_enabled True", "header_business_scenario Test"],
            ),
            (1, None, "Test", ["header_order 1", "header_business_scenario Test"]),
            (1, True, None, ["header_order 1", "header_is_compression_enabled True"]),
            (None, None, None, []),
        ],
    )
    def test_create_header(
        self,
        endpoint_mapper,
        order,
        is_compression_enabled,
        description,
        expected_headers,
        mocker,
    ):
        # Create a mock endpoint with the specified values
        mock_endpoint = mocker.MagicMock()
        mock_endpoint.order = order
        mock_endpoint.isCompressionEnabled = is_compression_enabled
        mock_endpoint.description = description

        # Act
        headers = endpoint_mapper._create_header(mock_endpoint)

        # Assert
        assert sorted(headers) == sorted(expected_headers)

    def test_map_to_endpoints_empty_list(
        self, endpoint_mapper, create_organization_record, create_organization_value
    ):
        # Arrange
        org_value = create_organization_value(endpoints=[])
        org_record = create_organization_record(org_value=org_value)

        # Act
        endpoints = endpoint_mapper.map_to_endpoints(org_record)

        # Assert
        assert endpoints == []

    def test_map_to_endpoints_multiple_endpoints(
        self,
        endpoint_mapper,
        create_organization_record,
        create_organization_value,
        create_endpoint_value,
    ):
        # Arrange
        endpoint1 = create_endpoint_value(
            endpoint_id="endpoint-123", connection_type="fhir"
        )
        endpoint2 = create_endpoint_value(
            endpoint_id="endpoint-456", connection_type="itk"
        )
        endpoint3 = create_endpoint_value(
            endpoint_id="endpoint-789", connection_type="email"
        )

        org_value = create_organization_value(
            endpoints=[endpoint1, endpoint2, endpoint3]
        )
        org_record = create_organization_record(org_value=org_value)

        # Act
        endpoints = endpoint_mapper.map_to_endpoints(org_record)

        # Assert
        assert len(endpoints) == 3
        assert endpoints[0].id == "endpoint-123"
        assert endpoints[0].connectionType.code == "hl7-fhir-rest"
        assert endpoints[1].id == "endpoint-456"
        assert endpoints[1].connectionType.code == "ihe-xcpd"
        assert endpoints[2].id == "endpoint-789"
        assert endpoints[2].connectionType.code == "direct-project"

    def test_map_to_endpoints_with_invalid_endpoints(
        self,
        endpoint_mapper,
        create_organization_record,
        create_organization_value,
        create_endpoint_value,
    ):
        # Arrange
        # Valid endpoint
        endpoint1 = create_endpoint_value(
            endpoint_id="endpoint-123", connection_type="fhir"
        )
        # Endpoint with unsupported connection type (still included but with connectionType=None)
        endpoint2 = create_endpoint_value(
            endpoint_id="endpoint-456", connection_type="unsupported"
        )

        org_value = create_organization_value(endpoints=[endpoint1, endpoint2])
        org_record = create_organization_record(org_value=org_value)

        # Act
        endpoints = endpoint_mapper.map_to_endpoints(org_record)

        # Assert
        assert len(endpoints) == 2
        assert endpoints[0].id == "endpoint-123"
        assert endpoints[0].connectionType is not None
        assert endpoints[1].id == "endpoint-456"
        assert endpoints[1].connectionType is None

    @pytest.mark.parametrize(
        ("connection_type", "format_type", "expected_mime_type", "expected_conn_code"),
        [
            ("fhir", "PDF", ["application/pdf"], "hl7-fhir-rest"),
            ("itk", "CDA", ["application/hl7-cda+xml"], "ihe-xcpd"),
            ("email", "FHIR", ["application/fhir+json"], "direct-project"),
            ("unknown", "PDF", ["application/pdf"], None),
            ("fhir", "unknown", [], "hl7-fhir-rest"),
            ("unknown", "unknown", [], None),
        ],
    )
    def test_combinations(
        self,
        endpoint_mapper,
        create_endpoint_value,
        create_organization_record,
        create_organization_value,
        connection_type,
        format_type,
        expected_mime_type,
        expected_conn_code,
    ):
        # Arrange
        endpoint_value = create_endpoint_value(
            connection_type=connection_type, format_type=format_type
        )
        org_value = create_organization_value(endpoints=[endpoint_value])
        org_record = create_organization_record(org_value=org_value)

        # Act
        endpoints = endpoint_mapper.map_to_endpoints(org_record)

        # Assert
        assert len(endpoints) == 1
        if expected_conn_code:
            assert endpoints[0].connectionType.code == expected_conn_code
        else:
            assert endpoints[0].connectionType is None
        assert endpoints[0].payloadMimeType == expected_mime_type
