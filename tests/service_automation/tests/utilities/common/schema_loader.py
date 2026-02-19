"""OpenAPI specification loading and validation fixtures."""

from pathlib import Path

import pytest
import yaml

from utilities.common.oas_validator import OASValidator

# Path to OAS schemas directory
OAS_SCHEMAS_DIR = Path(__file__).parent.parent.parent / "oas_schemas"
DEFAULT_OAS_SPEC = OAS_SCHEMAS_DIR / "openapi.yaml"


@pytest.fixture(scope="module")
def oas_spec() -> dict:
    """Load the OpenAPI specification as a dictionary."""
    with open(DEFAULT_OAS_SPEC, "r") as spec_file:
        return yaml.safe_load(spec_file)


@pytest.fixture(scope="module")
def oas_validator() -> OASValidator:
    """Provide an OAS validator instance for schema validation."""
    return OASValidator(DEFAULT_OAS_SPEC)


@pytest.fixture(scope="module")
def organization_schema(oas_validator: OASValidator) -> dict:
    """Get the Organization schema from the OAS spec."""
    return oas_validator.get_schema("Organization")


@pytest.fixture(scope="module")
def bundle_schema(oas_validator: OASValidator) -> dict:
    """Get the Bundle schema from the OAS spec."""
    return oas_validator.get_schema("Bundle")


@pytest.fixture(scope="module")
def operation_outcome_schema(oas_validator: OASValidator) -> dict:
    """Get the OperationOutcome schema from the OAS spec."""
    return oas_validator.get_schema("OperationOutcome")


@pytest.fixture(scope="module")
def organization_affiliation_schema(oas_validator: OASValidator) -> dict:
    """Get the OrganizationAffiliation schema from the OAS spec."""
    return oas_validator.get_schema("OrganizationAffiliation")
