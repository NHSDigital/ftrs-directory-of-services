from datetime import datetime

import pytest
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.endpoint import Endpoint
from services.ftrs_service.fhir_mapper.endpoint_mapper import EndpointMapper
from services.ftrs_service.repository.dynamo import (
    EndpointValue,
    OrganizationRecord,
    OrganizationValue,
)


@pytest.fixture
def endpoint_value():
    return EndpointValue(
        id="endpoint-123",
        identifier_oldDoS_id=9876,
        connectionType="fhir",
        managedByOrganisation="org-123",
        payloadType="document",
        format="PDF",
        address="https://example.org/fhir",
        order=1,
        isCompressionEnabled=True,
        description="Test scenario",
        status="active",
        createdBy="test-user",
        modifiedBy="test-user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedDateTime=datetime(2023, 1, 2),
    )


@pytest.fixture
def organization_record(endpoint_value):
    org_value = OrganizationValue(
        id="org-123",
        name="Test Organization",
        type="prov",
        active=True,
        identifier_ODS_ODSCode="O123",
        telecom="01234567890",
        endpoints=[endpoint_value],
        createdBy="test-user",
        modifiedBy="test-user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedDateTime=datetime(2023, 1, 2),
    )
    return OrganizationRecord(
        id="org-123",
        ods_code="O123",
        field="organization",
        value=org_value,
    )


@pytest.fixture
def endpoint_mapper():
    return EndpointMapper()


def test_map_to_endpoints(endpoint_mapper, organization_record):
    # Act
    endpoints = endpoint_mapper.map_to_endpoints(organization_record)

    # Assert
    assert len(endpoints) == 1
    assert isinstance(endpoints[0], Endpoint)
    assert endpoints[0].id == "endpoint-123"
    assert endpoints[0].status == "active"
    assert endpoints[0].connectionType.code == "hl7-fhir-rest"
    assert endpoints[0].managingOrganization.reference == "Organization/org-123"


def test_create_endpoint(endpoint_mapper, endpoint_value):
    # Act
    endpoint = endpoint_mapper._create_endpoint(endpoint_value)

    # Assert
    assert endpoint.id == "endpoint-123"
    assert endpoint.status == "active"
    assert endpoint.connectionType.code == "hl7-fhir-rest"
    assert endpoint.managingOrganization.reference == "Organization/org-123"
    assert endpoint.address == "https://example.org/fhir"
    assert len(endpoint.payloadType) == 1
    assert endpoint.payloadType[0].coding[0].code == "document"
    assert endpoint.payloadMimeType == ["application/pdf"]
    assert "header_order 1" in endpoint.header
    assert "header_is_compression_enabled True" in endpoint.header
    assert "header_business_scenario Test scenario" in endpoint.header


def test_create_connection_type_fhir(endpoint_mapper, endpoint_value):
    # Act
    connection_type = endpoint_mapper._create_connection_type(endpoint_value)

    # Assert
    assert (
        connection_type.system
        == "http://terminology.hl7.org/CodeSystem/endpoint-connection-type"
    )
    assert connection_type.code == "hl7-fhir-rest"


def test_create_connection_type_itk(endpoint_mapper, endpoint_value):
    # Arrange
    updated_endpoint = EndpointValue(
        **{**endpoint_value.model_dump(), "connectionType": "itk"}
    )

    # Act
    connection_type = endpoint_mapper._create_connection_type(updated_endpoint)

    # Assert
    assert connection_type.code == "ihe-xcpd"


def test_create_connection_type_email(endpoint_mapper, endpoint_value):
    # Arrange
    updated_endpoint = EndpointValue(
        **{**endpoint_value.model_dump(), "connectionType": "email"}
    )

    # Act
    connection_type = endpoint_mapper._create_connection_type(updated_endpoint)

    # Assert
    assert connection_type.code == "direct-project"


def test_create_connection_type_unsupported(endpoint_mapper, endpoint_value):
    # Arrange
    updated_endpoint = EndpointValue(
        **{**endpoint_value.model_dump(), "connectionType": "unsupported"}
    )

    # Act
    connection_type = endpoint_mapper._create_connection_type(updated_endpoint)

    # Assert
    assert connection_type is None


def test_determine_payload_mime_type_pdf(endpoint_mapper, endpoint_value):
    # Act
    mime_type = endpoint_mapper._determine_payload_mime_type(endpoint_value)

    # Assert
    assert mime_type == ["application/pdf"]


def test_determine_payload_mime_type_cda(endpoint_mapper, endpoint_value):
    # Arrange
    updated_endpoint = EndpointValue(**{**endpoint_value.model_dump(), "format": "CDA"})

    # Act
    mime_type = endpoint_mapper._determine_payload_mime_type(updated_endpoint)

    # Assert
    assert mime_type == ["application/hl7-cda+xml"]


def test_determine_payload_mime_type_fhir(endpoint_mapper, endpoint_value):
    # Arrange
    updated_endpoint = EndpointValue(
        **{**endpoint_value.model_dump(), "format": "FHIR"}
    )

    # Act
    mime_type = endpoint_mapper._determine_payload_mime_type(updated_endpoint)

    # Assert
    assert mime_type == ["application/fhir+json"]


def test_determine_payload_mime_type_unsupported(endpoint_mapper, endpoint_value):
    # Arrange
    updated_endpoint = EndpointValue(
        **{**endpoint_value.model_dump(), "format": "UNSUPPORTED"}
    )

    # Act
    mime_type = endpoint_mapper._determine_payload_mime_type(updated_endpoint)

    # Assert
    assert mime_type == []


def test_create_payload_type(endpoint_mapper, endpoint_value):
    # Act
    payload_type = endpoint_mapper._create_payload_type(endpoint_value)

    # Assert
    assert len(payload_type) == 1
    assert isinstance(payload_type[0], CodeableConcept)
    assert len(payload_type[0].coding) == 1
    assert (
        payload_type[0].coding[0].system
        == "http://hl7.org/fhir/ValueSet/endpoint-payload-type"
    )
    assert payload_type[0].coding[0].code == "document"


def test_create_payload_type_empty(endpoint_mapper, endpoint_value):
    # Arrange
    # Since we can't directly set None to payloadType (would cause validation error),
    # create a custom test method that bypasses the field validator
    def _create_payload_type_with_none(mapper, endpoint):
        # Create a mock endpoint with None payloadType for testing only
        class MockEndpoint:
            pass

        mock = MockEndpoint()
        mock.payloadType = None
        return mapper._create_payload_type(mock)

    # Act
    payload_type = _create_payload_type_with_none(endpoint_mapper, endpoint_value)

    # Assert
    assert payload_type == []


def test_create_header(endpoint_mapper, endpoint_value):
    # Act
    headers = endpoint_mapper._create_header(endpoint_value)

    # Assert
    assert len(headers) == 3
    assert "header_order 1" in headers
    assert "header_is_compression_enabled True" in headers
    assert "header_business_scenario Test scenario" in headers


def test_create_header_with_none_values(endpoint_mapper, endpoint_value):
    # Similar to the test_create_payload_type_empty approach, we need a custom test
    # function for testing this behavior since we can't set None directly
    def _create_header_with_some_nones(mapper, endpoint):
        # Create a mock endpoint with some None values for testing only
        class MockEndpoint:
            pass

        mock = MockEndpoint()
        mock.order = None
        mock.isCompressionEnabled = None
        mock.description = "Test scenario"
        return mapper._create_header(mock)

    # Act
    headers = _create_header_with_some_nones(endpoint_mapper, endpoint_value)

    # Assert
    assert len(headers) == 1
    assert "header_business_scenario Test scenario" in headers


def test_map_to_endpoints_with_multiple_endpoints(endpoint_mapper, organization_record):
    # Arrange
    second_endpoint = EndpointValue(
        id="endpoint-456",
        identifier_oldDoS_id=5432,
        connectionType="email",
        managedByOrganisation="org-123",
        payloadType="document",
        format="CDA",
        address="mailto:test@example.org",
        order=2,
        isCompressionEnabled=False,
        description="Email scenario",
        status="active",
        createdBy="test-user",
        modifiedBy="test-user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedDateTime=datetime(2023, 1, 2),
    )

    # Create a new organization record with both endpoints
    updated_org_value = OrganizationValue(
        **{
            **organization_record.value.model_dump(),
            "endpoints": [organization_record.value.endpoints[0], second_endpoint],
        }
    )

    updated_org_record = OrganizationRecord(
        **{**organization_record.model_dump(), "value": updated_org_value}
    )

    # Act
    endpoints = endpoint_mapper.map_to_endpoints(updated_org_record)

    # Assert
    assert len(endpoints) == 2
    assert endpoints[0].id == "endpoint-123"
    assert endpoints[1].id == "endpoint-456"
    assert endpoints[1].connectionType.code == "direct-project"
    assert endpoints[1].payloadMimeType == ["application/hl7-cda+xml"]


def test_map_to_endpoints_with_unsupported_connection_type(
    endpoint_mapper, organization_record
):
    # Arrange
    unsupported_endpoint = EndpointValue(
        **{
            **organization_record.value.endpoints[0].model_dump(),
            "connectionType": "unsupported",
        }
    )

    # Create a new organization record with the unsupported endpoint
    updated_org_value = OrganizationValue(
        **{
            **organization_record.value.model_dump(),
            "endpoints": [unsupported_endpoint],
        }
    )

    updated_org_record = OrganizationRecord(
        **{**organization_record.model_dump(), "value": updated_org_value}
    )

    # Act - this should still return an endpoint even with unsupported connection type
    endpoints = endpoint_mapper.map_to_endpoints(updated_org_record)

    # Assert
    assert len(endpoints) == 1
    assert endpoints[0].connectionType is None
