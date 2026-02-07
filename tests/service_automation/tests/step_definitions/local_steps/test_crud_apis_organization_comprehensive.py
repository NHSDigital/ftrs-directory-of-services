"""Comprehensive local integration tests for CRUD APIs Organization endpoint.

These tests mirror the full AWS test coverage from organization_api.feature,
running against LocalStack with testcontainers. This provides ~100+ test cases
covering all Organization API functionality without requiring AWS deployment.

Usage:
    USE_LOCALSTACK=true pytest tests/step_definitions/local_steps/test_crud_apis_organization_comprehensive.py -v

Test Categories:
    - Basic CRUD operations
    - Name sanitization (title case, acronym preservation)
    - Role validation (primary/non-primary combinations)
    - Telecom validation (phone, email, URL)
    - Identifier validation (ODS code format)
    - Legal dates validation
    - Error handling (missing fields, invalid content-type)
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Generator
from uuid import uuid4

import boto3
import pytest
import requests
from testcontainers.localstack import LocalStackContainer

try:
    from ftrs_common.utils.db_service import reset_settings
except ImportError:  # pragma: no cover
    reset_settings = None

try:
    from ftrs_data_layer.domain import Organisation
    from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
except ImportError:  # pragma: no cover
    Organisation = None  # type: ignore[assignment]
    AttributeLevelRepository = None  # type: ignore[assignment]

# Path to JSON test data files
JSON_FILES_PATH = Path(__file__).parent.parent.parent / "json_files"

pytestmark = [pytest.mark.local, pytest.mark.crud_apis_local_comprehensive]


def is_local_test_mode() -> bool:
    """Check if tests should run in local mode."""
    return os.environ.get("USE_LOCALSTACK", "false").lower() == "true"


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def localstack_container() -> Generator[LocalStackContainer, None, None]:
    """Start LocalStack container for the test module."""
    if not is_local_test_mode():
        pytest.skip("Set USE_LOCALSTACK=true to run local integration tests")

    container = LocalStackContainer(image="localstack/localstack:3.0")
    container.start(timeout=120)  # Increased timeout for CI runners
    try:
        yield container
    finally:
        container.stop()


@pytest.fixture(scope="module")
def localstack_endpoint(localstack_container: LocalStackContainer) -> str:
    """Get the LocalStack endpoint URL."""
    return localstack_container.get_url()


@pytest.fixture(scope="module")
def configure_environment(
    localstack_endpoint: str,
) -> Generator[dict[str, str], None, None]:
    """Configure environment variables for LocalStack."""
    if reset_settings is not None:
        reset_settings()

    original_env = {
        "ENDPOINT_URL": os.environ.get("ENDPOINT_URL"),
        "AWS_ENDPOINT_URL": os.environ.get("AWS_ENDPOINT_URL"),
        "PROJECT_NAME": os.environ.get("PROJECT_NAME"),
        "ENVIRONMENT": os.environ.get("ENVIRONMENT"),
        "WORKSPACE": os.environ.get("WORKSPACE"),
        "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION"),
    }

    os.environ["ENDPOINT_URL"] = localstack_endpoint
    os.environ["AWS_ENDPOINT_URL"] = localstack_endpoint
    os.environ["PROJECT_NAME"] = "ftrs-dos"
    os.environ["ENVIRONMENT"] = "local"
    os.environ["WORKSPACE"] = "test"
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"

    yield {
        "endpoint_url": localstack_endpoint,
        "project": "ftrs-dos",
        "environment": "local",
        "workspace": "test",
    }

    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    if reset_settings is not None:
        reset_settings()


@pytest.fixture(scope="module")
def dynamodb_client(configure_environment: dict[str, str]) -> Any:
    """Create a DynamoDB client for LocalStack."""
    return boto3.client(
        "dynamodb",
        endpoint_url=configure_environment["endpoint_url"],
        region_name="eu-west-2",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@pytest.fixture(scope="module")
def dynamodb_tables(
    dynamodb_client: Any, configure_environment: dict[str, str]
) -> dict[str, str]:
    """Create DynamoDB tables for CRUD APIs testing."""
    project = configure_environment["project"]
    env = configure_environment["environment"]
    workspace = configure_environment["workspace"]

    tables = {
        "organisation": f"{project}-{env}-database-organisation-{workspace}",
        "location": f"{project}-{env}-database-location-{workspace}",
        "healthcare-service": f"{project}-{env}-database-healthcare-service-{workspace}",
    }

    for table_type, table_name in tables.items():
        try:
            key_schema = [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ]
            attribute_defs = [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
            ]
            gsi = []

            if table_type == "organisation":
                attribute_defs.append(
                    {"AttributeName": "identifier_ODS_ODSCode", "AttributeType": "S"}
                )
                gsi.append(
                    {
                        "IndexName": "OdsCodeValueIndex",
                        "KeySchema": [
                            {
                                "AttributeName": "identifier_ODS_ODSCode",
                                "KeyType": "HASH",
                            }
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                    }
                )

            create_params = {
                "TableName": table_name,
                "KeySchema": key_schema,
                "AttributeDefinitions": attribute_defs,
                "BillingMode": "PAY_PER_REQUEST",
            }
            if gsi:
                create_params["GlobalSecondaryIndexes"] = gsi

            dynamodb_client.create_table(**create_params)
        except dynamodb_client.exceptions.ResourceInUseException:
            pass

    return tables


def load_organisation_payload() -> dict[str, Any]:
    """Load the base organisation payload from JSON file."""
    file_path = JSON_FILES_PATH / "Organisation" / "organisation-payload.json"
    return json.loads(file_path.read_text())


def load_organisation_from_json(json_file: str) -> dict[str, Any]:
    """Load organisation data from a JSON test file."""
    file_path = JSON_FILES_PATH / json_file
    if not file_path.exists():
        raise FileNotFoundError(f"Test data file not found: {file_path}")
    return json.loads(file_path.read_text())


def seed_organisation_via_repository(
    table_name: str,
    endpoint_url: str,
    organisation_data: dict[str, Any],
) -> str:
    """Seed an organisation using the AttributeLevelRepository."""
    if Organisation is None or AttributeLevelRepository is None:
        pytest.skip("ftrs_data_layer is not available in this environment")

    repo = AttributeLevelRepository(
        table_name=table_name,
        model_cls=Organisation,
        endpoint_url=endpoint_url,
    )

    org = Organisation(**organisation_data)
    repo.create(org)
    return str(org.id)


def get_organisation_from_db(
    table_name: str,
    endpoint_url: str,
    org_id: str,
) -> Any:
    """Get an organisation from the database."""
    if Organisation is None or AttributeLevelRepository is None:
        pytest.skip("ftrs_data_layer is not available in this environment")

    repo = AttributeLevelRepository(
        table_name=table_name,
        model_cls=Organisation,
        endpoint_url=endpoint_url,
    )
    return repo.get(org_id)


@pytest.fixture(scope="module")
def crud_api_server(
    configure_environment: dict[str, str],
    dynamodb_tables: dict[str, str],
) -> Generator[dict[str, Any], None, None]:
    """Start the CRUD APIs server as a subprocess."""
    endpoint_url = configure_environment["endpoint_url"]

    repo_root = Path(__file__).parent.parent.parent.parent.parent.parent
    crud_apis_dir = repo_root / "services" / "crud-apis"

    if not crud_apis_dir.exists():
        pytest.skip(f"CRUD APIs directory not found: {crud_apis_dir}")

    crud_apis_python = crud_apis_dir / ".venv" / "bin" / "python"
    if not crud_apis_python.exists():
        pytest.skip(f"CRUD APIs venv not found: {crud_apis_python}")

    env = os.environ.copy()
    env.update(
        {
            "ENDPOINT_URL": endpoint_url,
            "AWS_ENDPOINT_URL": endpoint_url,
            "PROJECT_NAME": "ftrs-dos",
            "ENVIRONMENT": "local",
            "WORKSPACE": "test",
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",
            "AWS_DEFAULT_REGION": "eu-west-2",
            "PYTHONPATH": str(crud_apis_dir),
        }
    )

    port = 8889
    process = subprocess.Popen(
        [
            str(crud_apis_python),
            "-m",
            "uvicorn",
            "handler_main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(crud_apis_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    base_url = f"http://127.0.0.1:{port}"

    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/docs", timeout=1)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.5)
    else:
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
        pytest.fail(
            f"CRUD APIs server failed to start.\n"
            f"stdout: {stdout.decode()}\n"
            f"stderr: {stderr.decode()}"
        )

    yield {
        "base_url": base_url,
        "process": process,
        "endpoint_url": endpoint_url,
        "tables": dynamodb_tables,
    }

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture
def seeded_organisation(
    crud_api_server: dict[str, Any],
) -> dict[str, Any]:
    """Seed a fresh test organisation for each test."""
    org_data = load_organisation_from_json(
        "Organisation/organisation-with-4-endpoints.json"
    )
    org_data["id"] = str(uuid4())
    org_data["identifier_ODS_ODSCode"] = f"TEST{str(uuid4())[:5].upper()}"

    seed_organisation_via_repository(
        table_name=crud_api_server["tables"]["organisation"],
        endpoint_url=crud_api_server["endpoint_url"],
        organisation_data=org_data,
    )
    return org_data


def build_fhir_payload(
    org_id: str,
    ods_code: str,
    name: str = "Test Organisation",
    active: bool = True,
    telecom: list | None = None,
    extensions: list | None = None,
) -> dict[str, Any]:
    """Build a FHIR Organization payload."""
    payload = {
        "resourceType": "Organization",
        "id": org_id,
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": ods_code,
            }
        ],
        "active": active,
        "name": name,
    }

    if telecom is not None:
        payload["telecom"] = telecom

    if extensions is not None:
        payload["extension"] = extensions
    else:
        # Default extension with valid role structure
        payload["extension"] = [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {"url": "instanceID", "valueInteger": 12345},
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                    "display": "PRESCRIBING COST CENTRE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {"url": "period", "valuePeriod": {"start": "2020-01-15"}},
                        ],
                    },
                    {"url": "active", "valueBoolean": True},
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {"url": "instanceID", "valueInteger": 12346},
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO76",
                                    "display": "GP PRACTICE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {"url": "period", "valuePeriod": {"start": "2020-01-15"}},
                        ],
                    },
                    {"url": "active", "valueBoolean": True},
                ],
            },
        ]

    return payload


def update_organisation(
    base_url: str,
    payload: dict[str, Any],
    content_type: str = "application/fhir+json",
) -> requests.Response:
    """Send PUT request to update an organisation."""
    org_id = payload.get("id")
    headers = {
        "Content-Type": content_type,
        "Accept": "application/fhir+json",
        "NHSE-Product-ID": "test-product-id",
    }
    return requests.put(
        f"{base_url}/Organization/{org_id}",
        json=payload,
        headers=headers,
    )


# ============================================================================
# Test Classes
# ============================================================================


class TestBasicCrudOperations:
    """Basic CRUD operations tests."""

    def test_retrieve_organizations(self, crud_api_server: dict[str, Any]) -> None:
        """Test GET /Organization returns a bundle."""
        response = requests.get(
            f"{crud_api_server['base_url']}/Organization",
            headers={"Accept": "application/fhir+json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("resourceType") == "Bundle"

    def test_retrieve_organization_by_id(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test GET /Organization/{id} returns the organisation."""
        org_id = seeded_organisation["id"]
        response = requests.get(
            f"{crud_api_server['base_url']}/Organization/{org_id}",
            headers={"Accept": "application/fhir+json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("id") == org_id

    def test_retrieve_nonexistent_organization(
        self, crud_api_server: dict[str, Any]
    ) -> None:
        """Test GET /Organization/{id} returns 404 for non-existent org."""
        fake_id = str(uuid4())
        response = requests.get(
            f"{crud_api_server['base_url']}/Organization/{fake_id}",
            headers={"Accept": "application/fhir+json"},
        )
        assert response.status_code == 404

    def test_update_organization_success(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test PUT /Organization/{id} updates successfully."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(org_id, ods_code, name="Updated Test Organisation")
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200
        data = response.json()
        assert data.get("resourceType") == "OperationOutcome"

    def test_update_with_identical_data(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test updating with identical data returns success with 'no changes' message."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(org_id, ods_code, name="Identical Data Test")
        # First update
        response1 = update_organisation(crud_api_server["base_url"], payload)
        assert response1.status_code == 200

        # Second update with same data
        response2 = update_organisation(crud_api_server["base_url"], payload)
        assert response2.status_code == 200
        data = response2.json()
        assert data.get("resourceType") == "OperationOutcome"

    def test_update_nonexistent_organization(
        self, crud_api_server: dict[str, Any]
    ) -> None:
        """Test PUT /Organization/{id} returns error for non-existent org."""
        fake_id = str(uuid4())
        payload = build_fhir_payload(fake_id, "TEST123", name="Test")
        response = update_organisation(crud_api_server["base_url"], payload)
        assert response.status_code in (404, 500)


class TestNameSanitization:
    """Tests for organization name sanitization (title case, acronym preservation)."""

    @pytest.mark.parametrize(
        ("input_name", "expected_name"),
        [
            ("nhs trust hospital", "NHS Trust Hospital"),
            ("LONDON GP SURGERY", "London GP Surgery"),
            ("the icb board", "The ICB Board"),
            ("local pcn practice", "Local PCN Practice"),
            ("Mixed Case nhs gp", "Mixed Case NHS GP"),
            ("NHS DIGITAL SERVICES", "NHS Digital Services"),
            ("ccg primary care", "CCG Primary Care"),
            ("community pharmacy nhs", "Community Pharmacy NHS"),
        ],
    )
    def test_name_title_case_with_acronym_preservation(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        input_name: str,
        expected_name: str,
    ) -> None:
        """Test that names are sanitized to title case with acronym preservation."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(org_id, ods_code, name=input_name)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200

        # Verify in database
        db_org = get_organisation_from_db(
            crud_api_server["tables"]["organisation"],
            crud_api_server["endpoint_url"],
            org_id,
        )
        assert db_org.name == expected_name

    def test_name_with_special_characters(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test organization names with special characters."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(
            org_id, ods_code, name="Medical Practice - !Covid Local"
        )
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200


class TestRoleValidation:
    """Tests for primary and non-primary role validation."""

    def _build_role_extension(
        self, primary_role: str, non_primary_roles: list[str]
    ) -> list[dict[str, Any]]:
        """Build role extensions for the payload."""
        extensions = []

        # Primary role
        if primary_role and primary_role != "None":
            extensions.append(
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                    "extension": [
                        {"url": "instanceID", "valueInteger": 12345},
                        {
                            "url": "roleCode",
                            "valueCodeableConcept": {
                                "coding": [
                                    {
                                        "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                        "code": primary_role,
                                        "display": "Primary Role",
                                    }
                                ]
                            },
                        },
                        {
                            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                            "extension": [
                                {
                                    "url": "dateType",
                                    "valueCoding": {
                                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                        "code": "Legal",
                                        "display": "Legal",
                                    },
                                },
                                {
                                    "url": "period",
                                    "valuePeriod": {"start": "2020-01-15"},
                                },
                            ],
                        },
                        {"url": "active", "valueBoolean": True},
                    ],
                }
            )

        # Non-primary roles
        for idx, role_code in enumerate(non_primary_roles):
            extensions.append(
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                    "extension": [
                        {"url": "instanceID", "valueInteger": 12346 + idx},
                        {
                            "url": "roleCode",
                            "valueCodeableConcept": {
                                "coding": [
                                    {
                                        "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                        "code": role_code,
                                        "display": f"Role {role_code}",
                                    }
                                ]
                            },
                        },
                        {
                            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                            "extension": [
                                {
                                    "url": "dateType",
                                    "valueCoding": {
                                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                        "code": "Legal",
                                        "display": "Legal",
                                    },
                                },
                                {
                                    "url": "period",
                                    "valuePeriod": {"start": "2020-01-15"},
                                },
                            ],
                        },
                        {"url": "active", "valueBoolean": True},
                    ],
                }
            )

        return extensions

    @pytest.mark.parametrize(
        ("primary_role", "non_primary_roles"),
        [
            ("RO177", ["RO76"]),
            ("RO177", ["RO76", "RO80"]),
            ("RO177", ["RO76", "RO87"]),
            ("RO177", ["RO76", "RO80", "RO87"]),
            ("RO177", ["RO76", "RO268"]),
        ],
    )
    def test_valid_role_combinations(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        primary_role: str,
        non_primary_roles: list[str],
    ) -> None:
        """Test valid primary and non-primary role combinations."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        extensions = self._build_role_extension(primary_role, non_primary_roles)
        payload = build_fhir_payload(org_id, ods_code, extensions=extensions)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200
        data = response.json()
        assert data.get("resourceType") == "OperationOutcome"

    @pytest.mark.parametrize(
        ("primary_role", "non_primary_roles"),
        [
            ("RO177", ["RO80"]),  # Missing required RO76
            ("RO177", ["RO80", "RO87"]),  # Missing required RO76
            ("RO182", []),  # Invalid primary role
            ("RO177", ["RO80", "RO80"]),  # Duplicate non-primary roles
            ("RO177", []),  # RO177 must have at least one non-primary role
        ],
    )
    def test_invalid_role_combinations(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        primary_role: str,
        non_primary_roles: list[str],
    ) -> None:
        """Test invalid primary and non-primary role combinations."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        extensions = self._build_role_extension(primary_role, non_primary_roles)
        payload = build_fhir_payload(org_id, ods_code, extensions=extensions)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422
        data = response.json()
        assert data.get("resourceType") == "OperationOutcome"


class TestTelecomValidation:
    """Tests for telecom (phone, email, URL) validation."""

    @pytest.mark.parametrize(
        "phone",
        [
            "0300 311 22 34",
            "+44 7900 000 001",
            "07900 000 001",
            "+44 (0) 7900 000001",
        ],
    )
    def test_valid_phone_numbers(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        phone: str,
    ) -> None:
        """Test valid phone numbers are accepted."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        telecom = [{"system": "phone", "value": phone, "use": "work"}]
        payload = build_fhir_payload(org_id, ods_code, telecom=telecom)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "phone",
        [
            "+++ABC123",
            "12345",
            "+9991234567890",
            "+1 415-555-2671x1234",
            "++14155552671",
            "+00000000000",
            "0300-311-22-34",
            "020;7972;3272",
            "+44/7911/123456",
        ],
    )
    def test_invalid_phone_numbers(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        phone: str,
    ) -> None:
        """Test invalid phone numbers are rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        telecom = [{"system": "phone", "value": phone, "use": "work"}]
        payload = build_fhir_payload(org_id, ods_code, telecom=telecom)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    @pytest.mark.parametrize(
        "email",
        [
            "test@nhs.net",
            "test12@gmail.com",
            "test12@yahoo.com",
            "test@company.co.uk",
            "TEST@COMPANY.CO.UK",
        ],
    )
    def test_valid_email_addresses(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        email: str,
    ) -> None:
        """Test valid email addresses are accepted."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        telecom = [{"system": "email", "value": email, "use": "work"}]
        payload = build_fhir_payload(org_id, ods_code, telecom=telecom)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "email",
        [
            "invalidemail.com",
            "plainaddress",
            "john..test@example.com",
            "@missinglocal.com",
            "username@.leadingdot.com",
            "user@invalid_domain.com",
            "user@domain",
            "user@domain.c",
        ],
    )
    def test_invalid_email_addresses(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        email: str,
    ) -> None:
        """Test invalid email addresses are rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        telecom = [{"system": "email", "value": email, "use": "work"}]
        payload = build_fhir_payload(org_id, ods_code, telecom=telecom)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    @pytest.mark.parametrize(
        "url",
        [
            "http://example.com",
            "https://example.com",
            "HTTPS://EXAMPLE.COM",
        ],
    )
    def test_valid_urls(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        url: str,
    ) -> None:
        """Test valid URLs are accepted."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        telecom = [{"system": "url", "value": url, "use": "work"}]
        payload = build_fhir_payload(org_id, ods_code, telecom=telecom)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "url",
        [
            "htp://example.com",
            "http://exa mple.com",
            "http://example.com:99999",
        ],
    )
    def test_invalid_urls(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        url: str,
    ) -> None:
        """Test invalid URLs are rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        telecom = [{"system": "url", "value": url, "use": "work"}]
        payload = build_fhir_payload(org_id, ods_code, telecom=telecom)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    def test_empty_telecom_list(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test empty telecom list is accepted."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(org_id, ods_code, telecom=[])
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200

    def test_missing_telecom_type(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test telecom without system type is rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        telecom = [{"value": "0300 311 22 34", "use": "work"}]  # Missing 'system'
        payload = build_fhir_payload(org_id, ods_code, telecom=telecom)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    def test_missing_telecom_value(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test telecom without value is rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        telecom = [{"system": "phone", "use": "work"}]  # Missing 'value'
        payload = build_fhir_payload(org_id, ods_code, telecom=telecom)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422


class TestIdentifierValidation:
    """Tests for ODS code identifier validation."""

    @pytest.mark.parametrize(
        "ods_code",
        [
            "Z9",
            "B76",
            "A123",
            "ABC123",
            "abcDEF",
            "abcDEF456",
            "XyZ789",
            "A1B2C3D4E5F6",
            "ABCDEFGHIJKL",
            "1234567890",
            "TEST123456",
            "CODE2025",
            "M2T8W",
            "01234",
            "T2Y1",
        ],
    )
    def test_valid_ods_codes(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        ods_code: str,
    ) -> None:
        """Test valid ODS code formats are accepted."""
        org_id = seeded_organisation["id"]

        payload = build_fhir_payload(org_id, ods_code)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "ods_code",
        [
            "",
            "1234567890123",  # Too long (13 chars)
            "TOOLONG123456",  # Too long
            "!ABC123",  # Special char at start
            "ABC123!",  # Special char at end
            "@#$%^&*",  # All special chars
            "ABC_123",  # Underscore
            "abc.def",  # Period
            "ABC 123",  # Space
            "ABC-123",  # Hyphen
        ],
    )
    def test_invalid_ods_codes(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        ods_code: str,
    ) -> None:
        """Test invalid ODS code formats are rejected."""
        org_id = seeded_organisation["id"]

        payload = build_fhir_payload(org_id, ods_code)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    def test_missing_identifier_system(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test identifier without system is rejected."""
        org_id = seeded_organisation["id"]

        payload = build_fhir_payload(org_id, "TEST123")
        payload["identifier"] = [{"value": "M2T8W", "use": "official"}]  # No system
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    def test_empty_identifier_array(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test empty identifier array is rejected."""
        org_id = seeded_organisation["id"]

        payload = build_fhir_payload(org_id, "TEST123")
        payload["identifier"] = []
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    def test_invalid_identifier_system(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test identifier with invalid system is rejected."""
        org_id = seeded_organisation["id"]

        payload = build_fhir_payload(org_id, "TEST123")
        payload["identifier"] = [
            {"system": "invalid-system", "value": "M2T8W", "use": "official"}
        ]
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422


class TestLegalDatesValidation:
    """Tests for legal dates (TypedPeriod extension) validation."""

    def _build_extension_with_dates(
        self, start_date: str | None, end_date: str | None
    ) -> list[dict[str, Any]]:
        """Build extension with specified legal dates."""
        period = {}
        if start_date:
            period["start"] = start_date
        if end_date:
            period["end"] = end_date

        return [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {"url": "instanceID", "valueInteger": 12345},
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                    "display": "PRESCRIBING COST CENTRE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {"url": "period", "valuePeriod": period},
                        ],
                    },
                    {"url": "active", "valueBoolean": True},
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {"url": "instanceID", "valueInteger": 12346},
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO76",
                                    "display": "GP PRACTICE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {"url": "period", "valuePeriod": period},
                        ],
                    },
                    {"url": "active", "valueBoolean": True},
                ],
            },
        ]

    @pytest.mark.parametrize(
        ("start_date", "end_date"),
        [
            ("2020-01-15", "2025-12-31"),
            ("2020-02-15", None),
            ("2020-01-15", "2024-12-31"),
            ("2020-02-29", "2028-02-29"),  # Leap year dates
        ],
    )
    def test_valid_legal_dates(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        start_date: str,
        end_date: str | None,
    ) -> None:
        """Test valid legal date combinations."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        extensions = self._build_extension_with_dates(start_date, end_date)
        payload = build_fhir_payload(org_id, ods_code, extensions=extensions)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "invalid_date",
        [
            "2020-13-45",  # Invalid month/day
            "20-01-2020",  # Wrong format
            "2020/01/15",  # Wrong separator
            "2020-1-5",  # Missing leading zeros
            "15-01-2020",  # DD-MM-YYYY
            "invalid",  # Not a date
        ],
    )
    def test_invalid_date_formats(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        invalid_date: str,
    ) -> None:
        """Test invalid date formats are rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        extensions = self._build_extension_with_dates(invalid_date, None)
        payload = build_fhir_payload(org_id, ods_code, extensions=extensions)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    def test_start_date_equals_end_date(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test start date matching end date is rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        extensions = self._build_extension_with_dates("2025-01-01", "2025-01-01")
        payload = build_fhir_payload(org_id, ods_code, extensions=extensions)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422


class TestErrorHandling:
    """Tests for error handling - missing fields, invalid content-type, etc."""

    @pytest.mark.parametrize(
        "missing_field",
        [
            "resourceType",
            "meta",
            "identifier",
            "name",
            "active",
        ],
    )
    def test_missing_required_field(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        missing_field: str,
    ) -> None:
        """Test missing required fields are rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(org_id, ods_code)
        del payload[missing_field]

        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422
        data = response.json()
        assert data.get("resourceType") == "OperationOutcome"

    def test_invalid_content_type(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test request with invalid Content-Type is rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(org_id, ods_code)
        response = update_organisation(
            crud_api_server["base_url"], payload, content_type="text/plain"
        )

        assert response.status_code == 415

    def test_unexpected_field_in_payload(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test unexpected field in payload is rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(org_id, ods_code)
        payload["unexpectedField"] = "unexpected value"

        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    @pytest.mark.parametrize(
        "active_value",
        [
            "",
            "null",
        ],
    )
    def test_invalid_active_field_values(
        self,
        crud_api_server: dict[str, Any],
        seeded_organisation: dict[str, Any],
        active_value: str,
    ) -> None:
        """Test invalid values for active field are rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(org_id, ods_code)
        payload["active"] = active_value

        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    def test_null_active_field(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test null active field is rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(org_id, ods_code)
        payload["active"] = None

        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422


class TestExtensionValidation:
    """Tests for extension structure validation."""

    def test_missing_role_code_extension(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test extension without roleCode is rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        extensions = [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {"url": "instanceID", "valueInteger": 12345},
                    # Missing roleCode
                    {"url": "active", "valueBoolean": True},
                ],
            }
        ]
        payload = build_fhir_payload(org_id, ods_code, extensions=extensions)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    def test_invalid_extension_url(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test extension with invalid URL is rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        extensions = [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole-INVALID",
                "extension": [
                    {"url": "instanceID", "valueInteger": 12345},
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                    "display": "PRESCRIBING COST CENTRE",
                                }
                            ]
                        },
                    },
                    {"url": "active", "valueBoolean": True},
                ],
            }
        ]
        payload = build_fhir_payload(org_id, ods_code, extensions=extensions)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422

    def test_empty_extension_url(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test extension with empty URL is rejected."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        extensions = [
            {
                "url": "",
                "extension": [
                    {"url": "instanceID", "valueInteger": 12345},
                ],
            }
        ]
        payload = build_fhir_payload(org_id, ods_code, extensions=extensions)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 422


class TestDatabaseConsistency:
    """Tests for database consistency after updates."""

    def test_database_reflects_updated_name(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test database reflects updated name after PUT."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        payload = build_fhir_payload(org_id, ods_code, name="Updated Name Test")
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200

        db_org = get_organisation_from_db(
            crud_api_server["tables"]["organisation"],
            crud_api_server["endpoint_url"],
            org_id,
        )
        assert db_org.name == "Updated Name Test"

    def test_database_reflects_updated_telecom(
        self, crud_api_server: dict[str, Any], seeded_organisation: dict[str, Any]
    ) -> None:
        """Test database reflects updated telecom after PUT."""
        org_id = seeded_organisation["id"]
        ods_code = seeded_organisation["identifier_ODS_ODSCode"]

        telecom = [{"system": "phone", "value": "0300 123 4567", "use": "work"}]
        payload = build_fhir_payload(org_id, ods_code, telecom=telecom)
        response = update_organisation(crud_api_server["base_url"], payload)

        assert response.status_code == 200

        db_org = get_organisation_from_db(
            crud_api_server["tables"]["organisation"],
            crud_api_server["endpoint_url"],
            org_id,
        )
        assert db_org.telecom is not None
