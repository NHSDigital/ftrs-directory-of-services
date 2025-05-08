from datetime import datetime

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.organization import Organization

from functions.ftrs_service.fhir_mapper import BundleMapper
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
def bundle_mapper():
    return BundleMapper(base_url="https://example.org")


def test_map_to_fhir(bundle_mapper, organization_record, mocker):
    # Arrange
    org_resource = Organization(
        id="org-123",
        identifier=[
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "O123"}
        ],
        name="Test Organization",
    )
    endpoint_resource = Endpoint(
        id="endpoint-123",
        address="https://example.org/fhir",
        connectionType=Coding(
            system="http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
            code="hl7-fhir-rest",
        ),
        payloadType=[
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                        code="document",
                    )
                ]
            )
        ],
        status="active",
    )
    mocker.patch.object(
        bundle_mapper.organization_mapper,
        "map_to_organization_resource",
        return_value=org_resource,
    )
    mocker.patch.object(
        bundle_mapper.endpoint_mapper,
        "map_to_endpoints",
        return_value=[endpoint_resource],
    )

    # Act
    bundle = bundle_mapper.map_to_fhir(organization_record)

    # Assert
    assert isinstance(bundle, Bundle)
    assert bundle.type == "searchset"
    assert len(bundle.entry) == 2  # 1 endpoint + 1 organization
    assert bundle.entry[0].resource == endpoint_resource
    assert bundle.entry[1].resource == org_resource


def test_create_bundle(bundle_mapper):
    # Arrange
    org_resource = Organization(
        id="org-123",
        identifier=[
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "O123"}
        ],
        name="Test Organization",
    )
    endpoint_resource = Endpoint(
        id="endpoint-123",
        address="https://example.org/fhir",
        connectionType=Coding(
            system="http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
            code="hl7-fhir-rest",
        ),
        payloadType=[
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                        code="document",
                    )
                ]
            )
        ],
        status="active",
    )

    # Act
    bundle = bundle_mapper._create_bundle(org_resource, [endpoint_resource])

    # Assert
    assert isinstance(bundle, Bundle)
    assert bundle.type == "searchset"
    assert bundle.id is not None
    assert len(bundle.link) == 1
    assert bundle.link[0].relation == "self"
    assert "O123" in bundle.link[0].url
    assert len(bundle.entry) == 2
    assert bundle.entry[0].resource == endpoint_resource
    assert bundle.entry[1].resource == org_resource


def test_create_entry(bundle_mapper):
    # Arrange
    org_resource = Organization(
        id="org-123",
        name="Test Organization",
    )

    # Act
    entry = bundle_mapper._create_entry("Organization", org_resource, "include")

    # Assert
    assert entry["fullUrl"] == "https://example.org/Organization/org-123"
    assert entry["resource"] == org_resource
    assert entry["search"]["mode"] == "include"
