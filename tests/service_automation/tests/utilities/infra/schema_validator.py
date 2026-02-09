"""Utility for validating API responses against OpenAPI schemas."""

from typing import Any

import yaml
from jsonschema import Draft7Validator, RefResolver
from loguru import logger


def load_openapi_schema(schema_path: str) -> dict[str, Any]:
    """
    Load OpenAPI schema from YAML file.

    Args:
        schema_path: Path to the OpenAPI YAML schema file

    Returns:
        Parsed OpenAPI schema as a dictionary
    """
    with open(schema_path, "r") as schema_file:
        return yaml.safe_load(schema_file)


def get_response_schema(
    openapi_spec: dict[str, Any], path: str, method: str, status_code: str
) -> dict[str, Any] | None:
    """
    Extract response schema for a specific endpoint, method, and status code.

    Args:
        openapi_spec: The loaded OpenAPI specification
        path: The API path (e.g., "/Organization")
        method: HTTP method (e.g., "get", "post")
        status_code: HTTP status code (e.g., "200", "400")

    Returns:
        The response schema or None if not found
    """
    try:
        responses = openapi_spec["paths"][path][method.lower()]["responses"]
        response = responses[status_code]
        content = response["content"]["application/fhir+json"]
        schema = content["schema"]

        # Resolve $ref if present
        if "$ref" in schema:
            ref_path = schema["$ref"].split("/")[1:]  # Remove leading '#'
            resolved_schema = openapi_spec
            for key in ref_path:
                resolved_schema = resolved_schema[key]
            return resolved_schema

        return schema
    except KeyError as e:
        logger.error(f"Could not find schema: {e}")
        return None


def validate_response_against_schema(
    response_data: dict[str, Any], schema: dict[str, Any], openapi_spec: dict[str, Any]
) -> tuple[bool, str | None]:
    """
    Validate response data against a JSON schema with OpenAPI reference resolution.

    Args:
        response_data: The API response data to validate
        schema: The JSON schema to validate against
        openapi_spec: The full OpenAPI specification for resolving $ref

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Create a resolver that can handle $ref within the OpenAPI document
        resolver = RefResolver.from_schema(openapi_spec)

        # Create a validator with the resolver
        validator = Draft7Validator(schema, resolver=resolver)

        # Validate and collect errors
        errors = list(validator.iter_errors(response_data))

        if errors:
            error_messages = []
            for error in errors[:5]:  # Limit to first 5 errors
                path = ".".join(str(p) for p in error.path) if error.path else "root"
                error_messages.append(f"{path}: {error.message}")
            error_msg = "Schema validation failed:\n" + "\n".join(error_messages)
            logger.error(error_msg)
            return False, error_msg

        logger.info("Response successfully validated against schema")
        return True, None
    except Exception as e:
        error_msg = f"Schema validation error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def validate_api_response(
    response_data: dict[str, Any],
    schema_path: str,
    endpoint_path: str,
    method: str = "get",
    status_code: str = "200",
) -> tuple[bool, str | None]:
    """
    Complete validation of API response against OpenAPI schema.

    Args:
        response_data: The API response data to validate
        schema_path: Path to the OpenAPI YAML schema file
        endpoint_path: The API endpoint path
        method: HTTP method (default: "get")
        status_code: Expected status code (default: "200")

    Returns:
        Tuple of (is_valid, error_message)
    """
    openapi_spec = load_openapi_schema(schema_path)
    schema = get_response_schema(openapi_spec, endpoint_path, method, status_code)

    if schema is None:
        return (
            False,
            f"Could not find schema for {method.upper()} {endpoint_path} {status_code}",
        )

    return validate_response_against_schema(response_data, schema, openapi_spec)
