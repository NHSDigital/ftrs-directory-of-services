from datetime import datetime
from unittest.mock import patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.organization import Organization

from functions.ftrs_service.fhir_mapper.bundle_mapper import BundleMapper
from functions.ftrs_service.repository.dynamo import (
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
def organization_value(endpoint_value):
    return OrganizationValue(
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


@pytest.fixture
def organization_record(organization_value):
    return OrganizationRecord(
        id="org-123",
        ods_code="O123",
        field="organization",
        value=organization_value,
    )


@pytest.fixture
def bundle_mapper():
    return BundleMapper(base_url="https://example.org")


def test_map_to_fhir_with_no_endpoints(bundle_mapper, organization_record):
    # Arrange
    updated_org_value = OrganizationValue(
        **{**organization_record.value.model_dump(), "endpoints": []}
    )
    updated_org_record = OrganizationRecord(
        **{**organization_record.model_dump(), "value": updated_org_value}
    )

    # Create mock organization resource
    org_resource = Organization.model_validate(
        {
            "id": "org-123",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "O123",
                }
            ],
            "name": "Test Organization",
            "active": True,
        }
    )

    # Mock the mapper methods
    with patch.object(
        bundle_mapper.organization_mapper,
        "map_to_organization_resource",
        return_value=org_resource,
    ) as mock_org_mapper:
        with patch.object(
            bundle_mapper.endpoint_mapper, "map_to_endpoints", return_value=[]
        ) as mock_endpoint_mapper:
            # Act
            bundle = bundle_mapper.map_to_fhir(updated_org_record)

            # Assert
            mock_org_mapper.assert_called_once_with(updated_org_record)
            mock_endpoint_mapper.assert_called_once_with(updated_org_record)
            assert isinstance(bundle, Bundle)
            assert bundle.type == "searchset"
            assert len(bundle.entry) == 1  # Only organization, no endpoints
            assert bundle.entry[0].resource == org_resource


def test_map_to_fhir_with_multiple_endpoints(bundle_mapper, organization_record):
    # Arrange
    # Create two mock endpoint resources with required fields
    endpoint1 = Endpoint.model_validate(
        {
            "id": "endpoint-123",
            "status": "active",
            "connectionType": {
                "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                "code": "hl7-fhir-rest",
            },
            "payloadType": [
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                            "code": "document",
                        }
                    ]
                }
            ],
            "address": "https://example.org/fhir",
        }
    )

    endpoint2 = Endpoint.model_validate(
        {
            "id": "endpoint-456",
            "status": "active",
            "connectionType": {
                "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                "code": "hl7-fhir-rest",
            },
            "payloadType": [
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                            "code": "document",
                        }
                    ]
                }
            ],
            "address": "https://example.org/fhir2",
        }
    )

    # Create mock organization resource
    org_resource = Organization.model_validate(
        {
            "id": "org-123",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "O123",
                }
            ],
            "name": "Test Organization",
            "active": True,
        }
    )

    # Mock the mapper methods
    with patch.object(
        bundle_mapper.organization_mapper,
        "map_to_organization_resource",
        return_value=org_resource,
    ) as mock_org_mapper:
        with patch.object(
            bundle_mapper.endpoint_mapper,
            "map_to_endpoints",
            return_value=[endpoint1, endpoint2],
        ) as mock_endpoint_mapper:
            # Act
            bundle = bundle_mapper.map_to_fhir(organization_record)

            # Assert
            mock_org_mapper.assert_called_once_with(organization_record)
            mock_endpoint_mapper.assert_called_once_with(organization_record)
            assert isinstance(bundle, Bundle)
            assert bundle.type == "searchset"
            assert len(bundle.entry) == 3  # 2 endpoints + 1 organization
            assert bundle.entry[0].resource == endpoint1
            assert bundle.entry[1].resource == endpoint2
            assert bundle.entry[2].resource == org_resource


def test_create_entry_for_endpoint(bundle_mapper):
    # Arrange
    endpoint_resource = Endpoint.model_validate(
        {
            "id": "endpoint-123",
            "status": "active",
            "connectionType": {
                "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                "code": "hl7-fhir-rest",
            },
            "payloadType": [
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                            "code": "document",
                        }
                    ]
                }
            ],
            "address": "https://example.org/fhir",
        }
    )

    # Act
    entry = bundle_mapper._create_entry("Endpoint", endpoint_resource, "match")

    # Assert
    assert entry["fullUrl"] == "https://example.org/Endpoint/endpoint-123"
    assert entry["resource"] == endpoint_resource
    assert entry["search"]["mode"] == "match"


def test_create_bundle_with_invalid_organization(bundle_mapper):
    # Arrange: Create an Organization without an identifier
    org_resource = Organization.model_validate(
        {"id": "org-123", "name": "Test Organization", "active": True}
    )

    endpoint_resource = Endpoint.model_validate(
        {
            "id": "endpoint-123",
            "status": "active",
            "connectionType": {
                "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                "code": "hl7-fhir-rest",
            },
            "payloadType": [
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                            "code": "document",
                        }
                    ]
                }
            ],
            "address": "https://example.org/fhir",
        }
    )

    # Act & Assert - Use the correct exception type for when organization.identifier is None
    with pytest.raises(TypeError, match="'NoneType' object is not iterable"):
        bundle_mapper._create_bundle(org_resource, [endpoint_resource])


def test_create_bundle_with_custom_base_url():
    # Arrange
    custom_base_url = "https://custom-example.org"
    custom_mapper = BundleMapper(base_url=custom_base_url)

    org_resource = Organization.model_validate(
        {
            "id": "org-123",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "O123",
                }
            ],
            "name": "Test Organization",
            "active": True,
        }
    )

    endpoint_resource = Endpoint.model_validate(
        {
            "id": "endpoint-123",
            "status": "active",
            "connectionType": {
                "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                "code": "hl7-fhir-rest",
            },
            "payloadType": [
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                            "code": "document",
                        }
                    ]
                }
            ],
            "address": "https://example.org/fhir",
        }
    )

    # Act
    bundle = custom_mapper._create_bundle(org_resource, [endpoint_resource])

    # Assert
    assert custom_base_url in bundle.link[0].url
    assert bundle.entry[0].fullUrl == f"{custom_base_url}/Endpoint/endpoint-123"
    assert bundle.entry[1].fullUrl == f"{custom_base_url}/Organization/org-123"
