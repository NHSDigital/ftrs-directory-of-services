"""
Shared pytest fixtures for all test files.
This module provides reusable fixtures that can be used across all test files.
"""

# Standard library
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from uuid import UUID, uuid4

# Third-party
import pytest
from botocore.credentials import ReadOnlyCredentials
from fhir.resources.R4B.endpoint import Endpoint as FhirEndpoint
from fhir.resources.R4B.organization import Organization

# Local
from ftrs_data_layer.domain import Endpoint, Organisation, Telecom
from ftrs_data_layer.domain.enums import (
    EndpointBusinessScenario,
    EndpointConnectionType,
    EndpointPayloadMimeType,
    EndpointPayloadType,
    EndpointStatus,
    TelecomType,
)


@pytest.fixture
def create_endpoint():
    """Factory function to create Endpoint instances with customizable fields."""

    def _create_endpoint(
        endpoint_id: UUID | None = UUID("12345678123456781234567812345678"),
        identifier_old_dos_id: int = 123456,
        status: EndpointStatus = EndpointStatus.ACTIVE,
        connection_type: EndpointConnectionType = EndpointConnectionType.ITK,
        business_scenario: EndpointBusinessScenario = EndpointBusinessScenario.COPY,
        payload_mime_type: EndpointPayloadMimeType = EndpointPayloadMimeType.FHIR,
        is_compression_enabled: bool = True,
        managed_by_organisation=None,
        created_by: str = "test_user",
        created_date_time: datetime = datetime(2023, 10, 1),
        modified_by: str = "test_user",
        modified_date_time: datetime = datetime(2023, 10, 1),
        name: str = "Test Endpoint Name",
        payload_type: EndpointPayloadType = EndpointPayloadType.ED,
        service=None,
        address: str = "https://example.com/endpoint",
        order: int = 1,
    ) -> Endpoint:
        return Endpoint(
            id=endpoint_id or uuid4(),
            identifier_oldDoS_id=identifier_old_dos_id,
            status=status,
            connectionType=connection_type,
            businessScenario=business_scenario,
            payloadMimeType=payload_mime_type,
            isCompressionEnabled=is_compression_enabled,
            managedByOrganisation=managed_by_organisation or uuid4(),
            createdBy=created_by,
            createdDateTime=created_date_time,
            modifiedBy=modified_by,
            modifiedDateTime=modified_date_time,
            name=name,
            payloadType=payload_type,
            service=service,
            address=address,
            order=order,
        )

    return _create_endpoint


@pytest.fixture
def endpoint(create_endpoint):
    """Create a standard test Endpoint.
    Uses the create_endpoint factory function with default values."""
    return create_endpoint()


@pytest.fixture
def create_organisation():
    """Factory function to create Organisation instances with customizable fields."""

    def _create_organisation(
        org_id: UUID | None = None,
        identifier_ods_code: str = "123456",
        active: bool = True,
        name: str = "Test Organisation",
        telecom: list[Telecom] = [
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
        ],
        org_type: str = "GP Practice",
        created_by: str = "test_user",
        created_date_time: datetime = datetime(2023, 10, 1),
        modified_by: str = "test_user",
        modified_date_time: datetime = datetime(2023, 10, 1),
        endpoints: list[Endpoint] | None = None,
    ) -> Organisation:
        return Organisation(
            id=org_id or uuid4(),
            identifier_ODS_ODSCode=identifier_ods_code,
            active=active,
            name=name,
            telecom=telecom,
            type=org_type,
            createdBy=created_by,
            createdDateTime=created_date_time,
            modifiedBy=modified_by,
            modifiedDateTime=modified_date_time,
            endpoints=endpoints or [],
        )

    return _create_organisation


@pytest.fixture
def organisation(create_organisation, endpoint):
    """Create a standard test Organisation with the default Endpoint.
    Uses the create_organisation factory function with default values."""
    return create_organisation(endpoints=[endpoint])


@pytest.fixture
def create_fhir_organization():
    """Factory function to create FHIR Organization resources with customizable fields."""

    def _create_fhir_organization(
        org_id: str = "org-123",
        name: str = "Test Organization",
        ods_code: str = "O123",
        active: bool = True,
        telecom: str = "01234567890",
    ) -> Organization:
        return Organization.model_validate(
            {
                "id": org_id,
                "name": name,
                "active": active,
                "identifier": [
                    {
                        "use": "official",
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": ods_code,
                    }
                ],
                "telecom": [{"system": "phone", "value": telecom}],
                "address": [
                    {
                        "line": ["Dummy Medical Practice", "Dummy Street"],
                        "city": "Dummy City",
                        "postalCode": "DU00 0MY",
                        "country": "ENGLAND",
                    }
                ],
            }
        )

    return _create_fhir_organization


@pytest.fixture
def create_fhir_endpoint():
    """Factory function to create FHIR Endpoint resources with customizable fields."""

    def _create_fhir_endpoint(
        endpoint_id: str = "endpoint-123",
        status: str = "active",
        connection_type: str = "hl7-fhir-rest",
        managing_org_id: str = "org-123",
        payload_type: str = "document",
        address: str = "https://example.org/fhir",
    ) -> FhirEndpoint:
        return FhirEndpoint.model_validate(
            {
                "id": endpoint_id,
                "status": status,
                "connectionType": {
                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-EndpointConnection",
                    "code": connection_type,
                },
                "managingOrganization": {
                    "reference": f"Organization/{managing_org_id}"
                },
                "payloadType": [
                    {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                                "code": payload_type,
                            }
                        ]
                    }
                ],
                "address": address,
            }
        )

    return _create_fhir_endpoint


@pytest.fixture
def create_module() -> Any:
    """Load and return the create_open_search_index workflow module for tests.

    This keeps tests decoupled from import mechanics and mirrors how the
    module is used in workflows (file-based scripts).
    """
    repo_root = Path(__file__).resolve().parents[3]
    mod_path = repo_root / "scripts" / "workflow" / "create_open_search_index.py"
    name = "create_open_search_index"
    spec = importlib.util.spec_from_file_location(name, str(mod_path))
    if not spec or not spec.loader:
        raise RuntimeError()
    module = importlib.util.module_from_spec(spec)  # type: ignore
    # Make the module importable by name so tests and patch() can target it
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore
    return module


@pytest.fixture
def create_populate_module() -> Any:
    """Load and return the populate_open_search_index workflow module for tests.

    Registered under the name 'populate_open_search_index' so tests and patch()
    can reference it directly.
    """
    repo_root = Path(__file__).resolve().parents[3]
    mod_path = repo_root / "scripts" / "workflow" / "populate_open_search_index.py"
    name = "populate_open_search_index"
    spec = importlib.util.spec_from_file_location(name, str(mod_path))
    if not spec or not spec.loader:
        raise RuntimeError()
    module = importlib.util.module_from_spec(spec)  # type: ignore
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore
    return module


# Add missing fixtures required by open_search_index tests


@pytest.fixture
def fake_credentials() -> ReadOnlyCredentials:
    """Return a lightweight ReadOnlyCredentials object for signing tests."""
    # token=None is acceptable for tests that only need access/secret
    return ReadOnlyCredentials(
        access_key="AKIAFAKE", secret_key="FAKESECRET", token=None
    )


@pytest.fixture
def dummy_response() -> Callable[..., object]:
    """Factory that returns a Response-like object for tests.

    Usage: resp = dummy_response(status_code=201, text='{"ok":true}', headers={...}, reason='Created')
    """

    def _dummy(
        status_code: int = 200,
        text: str = "",
        headers: dict | None = None,
        reason: str = "",
    ):
        class Resp:
            def __init__(self):
                self.status_code = status_code
                self._text = text
                self.headers = headers or {}
                self.reason = reason

            @property
            def text(self) -> str:
                return self._text

            def json(self):
                if not self._text:
                    return {}
                try:
                    return json.loads(self._text)
                except (ValueError, json.JSONDecodeError):
                    return {}

        return Resp()

    return _dummy
