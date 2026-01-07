from datetime import UTC, datetime
from uuid import UUID

from freezegun import freeze_time
from ftrs_data_layer.domain import Endpoint
from ftrs_data_layer.domain.legacy.data_models import ServiceEndpointData

from common.mapping.endpoint import EndpointMapper
from service_migration.dependencies import ServiceMigrationDependencies


@freeze_time("2025-07-17T12:00:00")
def test_endpoint_mapper_map_http_endpoint(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that the endpoint mapper correctly maps an HTTP endpoint."""
    endpoint_data = ServiceEndpointData(
        id=12345,
        serviceid=1,
        endpointorder=1,
        transport="itk",
        format="xml",
        interaction="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        businessscenario="Primary",
        address="http://example.com/endpoint1",
        comment="Test Endpoint 1",
        iscompressionenabled="uncompressed",
    )

    mapper = EndpointMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    organisation_id = UUID("0fd917b6-608a-59a0-ba62-eba57ec06a0e")
    service_id = UUID("01d78de8-4e63-53b3-9b7d-107c39c23a8d")

    result = mapper.map(endpoint_data, organisation_id, service_id)

    assert isinstance(result, Endpoint)
    assert result.id == UUID("01d78de8-4e63-53b3-9b7d-107c39c23a8d")
    assert result.createdBy == "DATA_MIGRATION"
    assert result.createdDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert result.modifiedBy == "DATA_MIGRATION"
    assert result.modifiedDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert result.identifier_oldDoS_id == 12345
    assert result.status == "active"
    assert result.connectionType == "itk"
    assert result.name is None
    assert result.payloadMimeType == "xml"
    assert result.description == "Primary"
    assert (
        result.payloadType
        == "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0"
    )
    assert result.address == "http://example.com/endpoint1"
    assert result.managedByOrganisation == organisation_id
    assert result.service == service_id
    assert result.order == 1
    assert result.isCompressionEnabled is False


@freeze_time("2025-07-17T12:00:00")
def test_endpoint_mapper_map_telno_endpoint(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that the endpoint mapper correctly maps a telephone endpoint."""
    endpoint_data = ServiceEndpointData(
        id=67890,
        serviceid=1,
        endpointorder=2,
        transport="telno",
        format=None,
        interaction="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        businessscenario="Copy",
        address="tel:01234567890",
        comment="Test Endpoint 2",
        iscompressionenabled=None,
    )

    mapper = EndpointMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    organisation_id = UUID("0fd917b6-608a-59a0-ba62-eba57ec06a0e")
    service_id = UUID("4f1a685e-15da-5324-b596-6090fc90dc49")

    result = mapper.map(endpoint_data, organisation_id, service_id)

    assert isinstance(result, Endpoint)
    assert result.id == UUID("4f1a685e-15da-5324-b596-6090fc90dc49")
    assert result.createdBy == "DATA_MIGRATION"
    assert result.createdDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert result.modifiedBy == "DATA_MIGRATION"
    assert result.modifiedDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert result.identifier_oldDoS_id == 67890
    assert result.status == "active"
    assert result.connectionType == "telno"
    assert result.name is None
    assert result.payloadMimeType is None
    assert result.description == "Copy"
    assert result.payloadType is None
    assert result.address == "tel:01234567890"
    assert result.managedByOrganisation == organisation_id
    assert result.service == service_id
    assert result.order == 2
    assert result.isCompressionEnabled is False


@freeze_time("2025-07-17T12:00:00")
def test_endpoint_mapper_map_without_service_id(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that the endpoint mapper correctly maps an endpoint without a service ID."""
    endpoint_data = ServiceEndpointData(
        id=1,
        serviceid=1,
        endpointorder=1,
        transport="http",
        format=None,
        interaction="urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
        businessscenario="Primary",
        address="http://example.com/endpoint",
        comment="Test Endpoint",
        iscompressionenabled="compressed",
    )

    mapper = EndpointMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    organisation_id = UUID("4539600c-e04e-5b35-a582-9fb36858d0e0")

    result = mapper.map(endpoint_data, organisation_id)

    assert isinstance(result, Endpoint)
    assert result.service is None
    assert result.isCompressionEnabled is True


@freeze_time("2025-07-17T12:00:00")
def test_endpoint_mapper_map_payload_mime_type_mapping(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that the endpoint mapper correctly maps payload MIME types."""
    endpoint_data = ServiceEndpointData(
        id=1,
        serviceid=1,
        endpointorder=1,
        transport="email",
        format="text/html",
        interaction="urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
        businessscenario="Primary",
        address="mailto:test@example.com",
        comment="Test Endpoint",
        iscompressionenabled="uncompressed",
    )

    mapper = EndpointMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    organisation_id = UUID("4539600c-e04e-5b35-a582-9fb36858d0e0")

    result = mapper.map(endpoint_data, organisation_id)

    # Should use the format directly if not in mapping
    assert result.payloadMimeType == "text/html"
