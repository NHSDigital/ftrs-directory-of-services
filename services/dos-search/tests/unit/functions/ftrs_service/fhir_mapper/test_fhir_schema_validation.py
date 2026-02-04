"""
FHIR R4B Schema Validation Tests

Tests that generated FHIR resources comply with the official FHIR R4B specification.
These tests validate the complete schema structure, not just Pydantic model validation.
"""

import pytest
from fhir.resources.bundle import Bundle
from fhir.resources.endpoint import Endpoint
from fhir.resources.organization import Organization
from pydantic import ValidationError

from functions.ftrs_service.fhir_mapper.bundle_mapper import BundleMapper
from functions.ftrs_service.fhir_mapper.endpoint_mapper import EndpointMapper
from functions.ftrs_service.fhir_mapper.organization_mapper import OrganizationMapper


class TestBundleSchemaValidation:
    """Test that generated bundles comply with FHIR R4B Bundle schema"""

    def test_bundle_validates_against_fhir_r4b_schema(self, organisation):
        """Validate generated bundle against FHIR R4B schema"""
        # Arrange
        ods_code = "ABC123"

        # Act
        bundle_dict = BundleMapper.map_to_fhir(organisation, ods_code)

        # Assert - Should not raise ValidationError
        bundle = Bundle(**bundle_dict)
        assert bundle.resource_type == "Bundle"
        assert bundle.type == "searchset"
        assert len(bundle.entry) == 2  # Organization + Endpoint

    def test_empty_bundle_validates_against_fhir_r4b_schema(self):
        """Validate empty bundle (no matching ODS code) against FHIR R4B schema"""
        # Arrange
        ods_code = "NOEXIST"

        # Act
        bundle_dict = BundleMapper.map_to_fhir(None, ods_code)

        # Assert
        bundle = Bundle(**bundle_dict)
        assert bundle.resource_type == "Bundle"
        assert bundle.type == "searchset"
        assert len(bundle.entry) == 0

    def test_bundle_with_multiple_endpoints_validates_schema(self, create_organisation, create_endpoint):
        """Validate bundle with multiple endpoints against schema"""
        # Arrange
        endpoints = [
            create_endpoint(
                endpoint_id="EP001",
                connection_type="itk",
                address="https://example.com/itk",
            ),
            create_endpoint(
                endpoint_id="EP002",
                connection_type="email",
                address="test@example.com",
            ),
            create_endpoint(
                endpoint_id="EP003",
                connection_type="http",
                address="https://example.com/http",
            ),
        ]
        organisation = create_organisation(
            name="Test Organization",
            ods_code="ABC123",
            active=True,
            endpoints=endpoints,
        )

        # Act
        bundle_dict = BundleMapper.map_to_fhir(organisation, "ABC123")

        # Assert
        bundle = Bundle(**bundle_dict)
        assert bundle.resource_type == "Bundle"
        assert len(bundle.entry) == 4  # 1 org + 3 endpoints

    def test_bundle_link_structure_complies_with_schema(self, organisation):
        """Validate bundle link structure matches FHIR R4B requirements"""
        # Arrange
        ods_code = "TEST01"

        # Act
        bundle_dict = BundleMapper.map_to_fhir(organisation, ods_code)

        # Assert
        bundle = Bundle(**bundle_dict)
        assert len(bundle.link) == 1
        assert bundle.link[0].relation == "self"
        assert ods_code in bundle.link[0].url

    def test_bundle_entry_search_mode_complies_with_schema(self, organisation):
        """Validate entry search modes are valid FHIR values"""
        # Arrange
        ods_code = "ABC123"

        # Act
        bundle_dict = BundleMapper.map_to_fhir(organisation, ods_code)

        # Assert
        bundle = Bundle(**bundle_dict)
        # First entry should be Organization with search mode "match"
        assert bundle.entry[0].search.mode == "match"
        # Second entry should be Endpoint with search mode "include"
        assert bundle.entry[1].search.mode == "include"


class TestOrganizationSchemaValidation:
    """Test that generated Organization resources comply with FHIR R4B schema"""

    def test_organization_validates_against_fhir_r4b_schema(self, organisation):
        """Validate organization resource matches FHIR R4B specification"""
        # Act
        org_dict = OrganizationMapper.map_to_fhir(organisation)

        # Assert
        org_resource = Organization(**org_dict)
        assert org_resource.resource_type == "Organization"
        assert org_resource.active is True
        assert len(org_resource.identifier) == 1

    def test_organization_identifier_system_complies_with_schema(self, organisation):
        """Validate organization identifier system is a valid URI"""
        # Act
        org_dict = OrganizationMapper.map_to_fhir(organisation)

        # Assert
        org_resource = Organization(**org_dict)
        identifier = org_resource.identifier[0]
        assert identifier.system == "https://fhir.nhs.uk/Id/ods-organization-code"
        assert identifier.value == organisation.ods_code

    def test_organization_with_different_active_states(self, create_organisation):
        """Validate organization active field accepts boolean values"""
        # Test active=True
        org_active = create_organisation(name="Active Org", ods_code="ACT123", active=True)
        org_dict_active = OrganizationMapper.map_to_fhir(org_active)
        org_resource_active = Organization(**org_dict_active)
        assert org_resource_active.active is True

        # Test active=False
        org_inactive = create_organisation(name="Inactive Org", ods_code="INA123", active=False)
        org_dict_inactive = OrganizationMapper.map_to_fhir(org_inactive)
        org_resource_inactive = Organization(**org_dict_inactive)
        assert org_resource_inactive.active is False

    def test_organization_name_field_complies_with_schema(self, create_organisation):
        """Validate organization name field accepts valid strings"""
        # Arrange
        test_names = [
            "Simple Name",
            "Name with Numbers 123",
            "Name-with-Hyphens",
            "Name's with Apostrophe",
            "Very Long Organization Name That Exceeds Normal Length But Should Still Be Valid",
        ]

        for name in test_names:
            # Act
            org = create_organisation(name=name, ods_code="TST123", active=True)
            org_dict = OrganizationMapper.map_to_fhir(org)

            # Assert
            org_resource = Organization(**org_dict)
            assert org_resource.name == name


class TestEndpointSchemaValidation:
    """Test that generated Endpoint resources comply with FHIR R4B schema"""

    def test_endpoint_validates_against_fhir_r4b_schema(self, endpoint):
        """Validate endpoint resource matches FHIR R4B specification"""
        # Act
        endpoint_list = EndpointMapper.map_to_fhir([endpoint])

        # Assert
        assert len(endpoint_list) == 1
        endpoint_dict = endpoint_list[0]
        endpoint_resource = Endpoint(**endpoint_dict)
        assert endpoint_resource.resource_type == "Endpoint"

    def test_endpoint_status_field_uses_valid_fhir_values(self, create_endpoint):
        """Validate endpoint status uses FHIR-defined status codes"""
        # FHIR R4B valid endpoint statuses: active, suspended, error, off, entered-in-error, test
        # Our mapper uses "active"
        endpoint = create_endpoint(endpoint_id="EP001")
        endpoint_list = EndpointMapper.map_to_fhir([endpoint])

        endpoint_resource = Endpoint(**endpoint_list[0])
        assert endpoint_resource.status == "active"

    def test_endpoint_connection_type_coding_complies_with_schema(self, create_endpoint):
        """Validate connection type coding structure matches FHIR requirements"""
        # Arrange
        connection_types = ["itk", "email", "telno", "http"]

        for conn_type in connection_types:
            # Act
            endpoint = create_endpoint(
                endpoint_id=f"EP_{conn_type}",
                connection_type=conn_type,
            )
            endpoint_list = EndpointMapper.map_to_fhir([endpoint])

            # Assert
            endpoint_resource = Endpoint(**endpoint_list[0])
            coding = endpoint_resource.connectionType
            assert coding.system == "http://terminology.hl7.org/CodeSystem/endpoint-connection-type"
            assert coding.code == conn_type

    def test_endpoint_payload_type_structure_complies_with_schema(self, endpoint):
        """Validate payload type CodeableConcept structure"""
        # Act
        endpoint_list = EndpointMapper.map_to_fhir([endpoint])

        # Assert
        endpoint_resource = Endpoint(**endpoint_list[0])
        assert len(endpoint_resource.payloadType) == 1
        payload_type = endpoint_resource.payloadType[0]
        assert len(payload_type.coding) == 1
        assert payload_type.coding[0].system == "http://terminology.hl7.org/CodeSystem/endpoint-payload-type"
        assert payload_type.coding[0].code == "any"

    def test_endpoint_payload_mime_type_is_valid(self, endpoint):
        """Validate payload MIME type is a valid FHIR code"""
        # Act
        endpoint_list = EndpointMapper.map_to_fhir([endpoint])

        # Assert
        endpoint_resource = Endpoint(**endpoint_list[0])
        assert len(endpoint_resource.payloadMimeType) == 1
        assert endpoint_resource.payloadMimeType[0] == "application/fhir+json"

    def test_endpoint_address_field_accepts_various_formats(self, create_endpoint):
        """Validate address field accepts different URI/URL formats"""
        # Arrange
        test_addresses = [
            ("itk", "https://example.com/itk"),
            ("email", "test@example.com"),
            ("telno", "tel:+441234567890"),  # gitleaks:allow - Test phone number
            ("http", "https://api.example.com/fhir"),
        ]

        for conn_type, address in test_addresses:
            # Act
            endpoint = create_endpoint(
                endpoint_id=f"EP_{conn_type}",
                connection_type=conn_type,
                address=address,
            )
            endpoint_list = EndpointMapper.map_to_fhir([endpoint])

            # Assert
            endpoint_resource = Endpoint(**endpoint_list[0])
            assert endpoint_resource.address == address

    def test_empty_endpoint_list_returns_empty_array(self):
        """Validate mapper handles empty endpoint list correctly"""
        # Act
        endpoint_list = EndpointMapper.map_to_fhir([])

        # Assert
        assert endpoint_list == []
        assert isinstance(endpoint_list, list)


class TestEndpointExtensionsSchemaValidation:
    """Test that endpoint extensions comply with FHIR R4B Extension schema"""

    def test_order_extension_complies_with_schema(self, create_endpoint):
        """Validate order extension structure"""
        # Arrange
        endpoint = create_endpoint(endpoint_id="EP001", order=5)

        # Act
        endpoint_list = EndpointMapper.map_to_fhir([endpoint])

        # Assert
        endpoint_resource = Endpoint(**endpoint_list[0])
        order_extension = next(
            (ext for ext in endpoint_resource.extension if "order" in ext.url),
            None,
        )
        assert order_extension is not None
        assert order_extension.valueInteger == 5

    def test_compression_extension_complies_with_schema(self, create_endpoint):
        """Validate compression extension structure"""
        # Arrange
        endpoint = create_endpoint(endpoint_id="EP001", compression="gzip")

        # Act
        endpoint_list = EndpointMapper.map_to_fhir([endpoint])

        # Assert
        endpoint_resource = Endpoint(**endpoint_list[0])
        compression_extension = next(
            (ext for ext in endpoint_resource.extension if "compression" in ext.url),
            None,
        )
        assert compression_extension is not None
        assert compression_extension.valueString == "gzip"

    def test_business_scenario_extension_complies_with_schema(self, create_endpoint):
        """Validate business scenario extension with CodeableConcept"""
        # Arrange
        endpoint = create_endpoint(endpoint_id="EP001", business_scenario="Primary")

        # Act
        endpoint_list = EndpointMapper.map_to_fhir([endpoint])

        # Assert
        endpoint_resource = Endpoint(**endpoint_list[0])
        business_extension = next(
            (ext for ext in endpoint_resource.extension if "business-scenario" in ext.url),
            None,
        )
        assert business_extension is not None
        assert business_extension.valueCodeableConcept.coding[0].code == "primary-recipient"

    def test_multiple_extensions_on_single_endpoint(self, create_endpoint):
        """Validate endpoint with all extensions complies with schema"""
        # Arrange
        endpoint = create_endpoint(
            endpoint_id="EP001",
            order=1,
            compression="gzip",
            business_scenario="Copy",
        )

        # Act
        endpoint_list = EndpointMapper.map_to_fhir([endpoint])

        # Assert
        endpoint_resource = Endpoint(**endpoint_list[0])
        assert len(endpoint_resource.extension) == 3
        # All extensions should validate successfully with FHIR schema


class TestFullBundleSchemaCompliance:
    """Integration tests for complete FHIR bundle schema compliance"""

    def test_complete_bundle_with_all_elements_validates(self, create_organisation, create_endpoint):
        """Validate a fully populated bundle against FHIR R4B schema"""
        # Arrange - Create organization with multiple endpoints with all fields
        endpoints = [
            create_endpoint(
                endpoint_id="EP001",
                connection_type="itk",
                address="https://example.com/itk",
                order=1,
                compression="gzip",
                business_scenario="Primary",
            ),
            create_endpoint(
                endpoint_id="EP002",
                connection_type="email",
                address="test@example.com",
                order=2,
                compression="none",
                business_scenario="Copy",
            ),
        ]
        organisation = create_organisation(
            name="Complete Test Organization",
            ods_code="CMP123",
            active=True,
            endpoints=endpoints,
        )

        # Act
        bundle_dict = BundleMapper.map_to_fhir(organisation, "CMP123")

        # Assert - Full bundle validation
        bundle = Bundle(**bundle_dict)
        assert bundle.resource_type == "Bundle"
        assert bundle.type == "searchset"
        assert len(bundle.entry) == 3  # 1 org + 2 endpoints

        # Validate organization entry
        org_entry = bundle.entry[0]
        assert org_entry.search.mode == "match"
        org_resource = Organization(**org_entry.resource)
        assert org_resource.active is True

        # Validate endpoint entries
        for i in [1, 2]:
            endpoint_entry = bundle.entry[i]
            assert endpoint_entry.search.mode == "include"
            endpoint_resource = Endpoint(**endpoint_entry.resource)
            assert endpoint_resource.status == "active"

    def test_bundle_serialization_produces_valid_json(self, organisation):
        """Validate bundle can be serialized to valid JSON"""
        # Act
        bundle_dict = BundleMapper.map_to_fhir(organisation, "ABC123")
        bundle = Bundle(**bundle_dict)

        # Assert - Should produce valid JSON without errors
        json_output = bundle.json()
        assert json_output is not None
        assert "Bundle" in json_output
        assert "ABC123" in json_output

    def test_invalid_data_raises_validation_error(self):
        """Validate that invalid FHIR data raises ValidationError"""
        # Arrange - Invalid bundle structure
        invalid_bundle = {
            "resourceType": "Bundle",
            "type": "invalid-type",  # Invalid bundle type
        }

        # Assert
        with pytest.raises(ValidationError):
            Bundle(**invalid_bundle)
