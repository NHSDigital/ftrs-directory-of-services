"""OpenAPI Specification (OAS) validation utilities.

This module provides utilities to validate API responses against OpenAPI 3.0 schemas.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft4Validator
from jsonschema.validators import RefResolver
from loguru import logger


# Default OAS spec path
DEFAULT_OAS_SPEC_PATH = (
    Path(__file__).parent.parent.parent / "oas_schemas" / "openapi.yaml"
)


class OASValidator:
    """Validator for API responses against OpenAPI 3.0 schemas."""

    def __init__(self, spec_path: Path | str | None = None) -> None:
        """
        Initialize the OAS validator.

        Args:
            spec_path: Path to the OpenAPI spec file. Uses default if not provided.
        """
        self.spec_path = Path(spec_path) if spec_path else DEFAULT_OAS_SPEC_PATH
        self._spec: dict | None = None
        self._schemas: dict | None = None

    @property
    def spec(self) -> dict:
        """Load and cache the OpenAPI specification."""
        if self._spec is None:
            self._spec = self._load_spec()
        return self._spec

    @property
    def schemas(self) -> dict:
        """Get component schemas from the spec."""
        if self._schemas is None:
            self._schemas = self.spec.get("components", {}).get("schemas", {})
        return self._schemas

    def _load_spec(self) -> dict:
        """Load the OpenAPI spec from file."""
        logger.info(f"Loading OAS spec from: {self.spec_path}")
        with open(self.spec_path, "r") as f:
            return yaml.safe_load(f)

    def get_schema(self, schema_name: str) -> dict:
        """
        Get a specific schema from the OAS spec.

        Args:
            schema_name: Name of the schema (e.g., 'Organization', 'Bundle', 'OperationOutcome')

        Returns:
            The schema definition

        Raises:
            KeyError: If the schema is not found
        """
        if schema_name not in self.schemas:
            available = list(self.schemas.keys())
            raise KeyError(f"Schema '{schema_name}' not found. Available: {available}")
        return self.schemas[schema_name]

    def get_response_schema(
        self,
        path: str,
        method: str = "get",
        status_code: str = "200",
    ) -> dict | None:
        """
        Get the response schema for a specific endpoint.

        Args:
            path: API path (e.g., '/Organization')
            method: HTTP method (default: 'get')
            status_code: HTTP status code (default: '200')

        Returns:
            The response schema or None if not found
        """
        paths = self.spec.get("paths", {})
        path_item = paths.get(path, {})
        operation = path_item.get(method.lower(), {})
        responses = operation.get("responses", {})
        response = responses.get(str(status_code), {})
        content = response.get("content", {})

        for content_type, content_def in content.items():
            if "json" in content_type:
                return content_def.get("schema")

        return None

    def _resolve_ref(self, schema: dict) -> dict:
        """
        Resolve $ref references in a schema.

        Args:
            schema: Schema that may contain $ref

        Returns:
            Resolved schema
        """
        if "$ref" not in schema:
            return schema

        ref = schema["$ref"]
        # Handle local references like #/components/schemas/Organization
        if ref.startswith("#/components/schemas/"):
            schema_name = ref.split("/")[-1]
            return self.get_schema(schema_name)

        return schema

    def _build_resolver(self) -> RefResolver:
        """Build a JSON Schema resolver with the OAS spec as the base."""
        return RefResolver.from_schema(self.spec)

    def validate(
        self,
        data: dict | list,
        schema_name: str | None = None,
        schema: dict | None = None,
    ) -> list[str]:
        """
        Validate data against a schema.

        Args:
            data: The data to validate (typically a response body)
            schema_name: Name of the schema from components/schemas
            schema: Direct schema dict (takes precedence over schema_name)

        Returns:
            List of validation error messages (empty if valid)

        Raises:
            ValueError: If neither schema_name nor schema is provided
        """
        if schema is None and schema_name is None:
            raise ValueError("Either schema_name or schema must be provided")

        if schema is None:
            schema = self.get_schema(schema_name)

        # Resolve any $ref in the schema
        resolved_schema = self._resolve_ref(schema)

        # Build resolver for nested $refs
        resolver = self._build_resolver()

        validator = Draft4Validator(resolved_schema, resolver=resolver)
        errors: list[str] = []

        for error in validator.iter_errors(data):
            error_path = " -> ".join(str(p) for p in error.absolute_path) or "root"
            error_msg = f"[{error_path}] {error.message}"
            errors.append(error_msg)
            logger.warning(f"OAS validation error: {error_msg}")

        if errors:
            logger.error(f"OAS validation failed with {len(errors)} error(s)")
        else:
            logger.info("OAS validation passed")

        return errors

    def validate_response(
        self,
        response: Any,
        path: str,
        method: str = "get",
        status_code: int | str | None = None,
    ) -> list[str]:
        """
        Validate an API response against the expected schema.

        Args:
            response: API response object (must have .status and .json() method)
            path: API path (e.g., '/Organization')
            method: HTTP method (default: 'get')
            status_code: Expected status code (uses response.status if not provided)

        Returns:
            List of validation error messages (empty if valid)
        """
        actual_status = getattr(response, "status", None)
        expected_status = str(status_code) if status_code else str(actual_status)

        schema = self.get_response_schema(path, method, expected_status)

        if schema is None:
            logger.warning(
                f"No schema found for {method.upper()} {path} {expected_status}"
            )
            return [f"No schema defined for {method.upper()} {path} {expected_status}"]

        try:
            response_data = response.json()
        except Exception as e:
            return [f"Failed to parse response JSON: {e}"]

        logger.info(
            f"Validating response for {method.upper()} {path} "
            f"(status: {actual_status}) against schema"
        )

        return self.validate(response_data, schema=schema)

    def assert_valid(
        self,
        data: dict | list,
        schema_name: str | None = None,
        schema: dict | None = None,
    ) -> None:
        """
        Assert that data is valid against a schema.

        Args:
            data: The data to validate
            schema_name: Name of the schema from components/schemas
            schema: Direct schema dict

        Raises:
            AssertionError: If validation fails
        """
        errors = self.validate(data, schema_name=schema_name, schema=schema)
        if errors:
            error_details = "\n  - ".join(errors)
            raise AssertionError(f"OAS schema validation failed:\n  - {error_details}")

    def assert_response_valid(
        self,
        response: Any,
        path: str,
        method: str = "get",
        status_code: int | str | None = None,
    ) -> None:
        """
        Assert that an API response is valid against the expected schema.

        Args:
            response: API response object
            path: API path (e.g., '/Organization')
            method: HTTP method
            status_code: Expected status code

        Raises:
            AssertionError: If validation fails
        """
        errors = self.validate_response(response, path, method, status_code)
        if errors:
            error_details = "\n  - ".join(errors)
            raise AssertionError(
                f"OAS response validation failed:\n  - {error_details}"
            )


class _ValidatorHolder:
    """Holder class for the default validator instance to avoid global statement."""

    instance: OASValidator | None = None


def get_validator() -> OASValidator:
    """Get the default OAS validator instance (lazy initialization)."""
    if _ValidatorHolder.instance is None:
        _ValidatorHolder.instance = OASValidator()
    return _ValidatorHolder.instance


def validate_against_schema(
    data: dict | list,
    schema_name: str,
) -> list[str]:
    """
    Validate data against a named OAS schema.

    Args:
        data: The data to validate
        schema_name: Name of the schema (e.g., 'Organization', 'Bundle')

    Returns:
        List of validation error messages (empty if valid)
    """
    return get_validator().validate(data, schema_name=schema_name)


def validate_response(
    response: Any,
    path: str,
    method: str = "get",
    status_code: int | str | None = None,
) -> list[str]:
    """
    Validate an API response against the OAS spec.

    Args:
        response: API response object
        path: API path
        method: HTTP method
        status_code: Expected status code

    Returns:
        List of validation error messages (empty if valid)
    """
    return get_validator().validate_response(response, path, method, status_code)


def assert_schema_valid(data: dict | list, schema_name: str) -> None:
    """
    Assert that data is valid against a named OAS schema.

    Args:
        data: The data to validate
        schema_name: Name of the schema

    Raises:
        AssertionError: If validation fails
    """
    get_validator().assert_valid(data, schema_name=schema_name)


def assert_response_valid(
    response: Any,
    path: str,
    method: str = "get",
    status_code: int | str | None = None,
) -> None:
    """
    Assert that an API response is valid against the OAS spec.

    Args:
        response: API response object
        path: API path
        method: HTTP method
        status_code: Expected status code

    Raises:
        AssertionError: If validation fails
    """
    get_validator().assert_response_valid(response, path, method, status_code)
