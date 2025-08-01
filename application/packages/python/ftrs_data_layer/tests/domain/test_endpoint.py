from uuid import uuid4

from ftrs_data_layer.domain import Endpoint


def test_endpoint() -> None:
    endpoint = Endpoint(
        id=uuid4(),
        identifier_oldDoS_id=123456,
        status="active",
        connectionType="itk",
        description="Copy",
        payloadMimeType="application/fhir",
        identifier_oldDoS_uid="123456",
        isCompressionEnabled=True,
        managedByOrganisation=uuid4(),
        createdBy="test_user",
        createdDateTime="2023-10-01T00:00:00Z",
        modifiedBy="test_user",
        modifiedDateTime="2023-10-01T00:00:00Z",
        name="Test Endpoint Name",
        payloadType="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        service=None,
        address="https://example.com/endpoint",
        order=1,
    )

    assert endpoint.model_dump(mode="json") == {
        "id": str(endpoint.id),
        "identifier_oldDoS_id": 123456,
        "status": "active",
        "connectionType": "itk",
        "description": "Copy",
        "payloadMimeType": "application/fhir",
        "isCompressionEnabled": True,
        "managedByOrganisation": str(endpoint.managedByOrganisation),
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Endpoint Name",
        "payloadType": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        "service": None,
        "address": "https://example.com/endpoint",
        "order": 1,
    }
