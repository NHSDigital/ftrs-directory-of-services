import json
import re

from loguru import logger
from pytest_bdd import parsers, then


@then(parsers.parse('all "{resource_type}" entries have search mode "{mode}"'))
def api_check_entries_search_mode(fresponse, resource_type: str, mode: str):
    """Verify all entries of a specific resource type have the expected search mode."""
    response = fresponse.json()
    matching_entries = [
        entry
        for entry in response.get("entry", [])
        if entry.get("resource", {}).get("resourceType") == resource_type
    ]
    assert len(matching_entries) > 0, (
        f"No entries found with resourceType '{resource_type}'"
    )
    for entry in matching_entries:
        actual_mode = entry.get("search", {}).get("mode")
        assert actual_mode == mode, (
            f"Expected search mode '{mode}' for {resource_type} but got '{actual_mode}'"
        )


@then(
    parsers.parse(
        'the "{resource_type}" resource has "{array_name}" array containing "{array_item}" with value "{expected_value}"'
    )
)
def api_check_resource_type_str_use(
    fresponse, resource_type: str, array_name: str, array_item: str, expected_value: str
):
    """Verify identifier[0].use field."""
    response = fresponse.json()
    resource_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource_type
    ]
    assert len(resource_entries) > 0, f"No {resource_type} resource found"
    resource = resource_entries[0]["resource"]
    array = resource.get(array_name, [{}])[0]
    actual_value = array.get(array_item)
    assert actual_value == expected_value, (
        f"Expected {array_name}[0].{array_item} '{expected_value}' but got '{actual_value}'"
    )


@then(
    parsers.parse(
        'the "{resource_type}" resource has "{field_name}" field with value "{expected_value}"'
    )
)
def api_check_resource_type_field_value(
    fresponse, resource_type: str, field_name: str, expected_value: str
):
    """Verify {resource_type}.{field_name} has the expected value."""
    response = fresponse.json()
    resource_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource_type
    ]
    assert len(resource_entries) > 0, f"No {resource_type} resource found"
    resource = resource_entries[0]["resource"]
    logger.info(f"Checking {resource_type}.{field_name} value. Resource: {resource}")
    actual_value = resource.get(field_name)
    logger.info(f"actual value='{actual_value}'")
    assert actual_value == expected_value, (
        f"Expected {resource_type}.{field_name} '{expected_value}' but got '{actual_value}'"
    )


@then(
    parsers.parse(
        'the "{resource_type}" resource has "{field_name}" field with boolean {expected_value}'
    )
)
def api_check_resource_type_boolean_value(
    fresponse, resource_type: str, field_name: str, expected_value: str
):
    """Verify {resource_type}.{field_name} has the expected boolean value.
    Accepts 'true' or 'false' (case-insensitive).
    """
    expected_bool = expected_value == "true"
    response = fresponse.json()
    resource_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource_type
    ]
    assert len(resource_entries) > 0, f"No {resource_type} resource found"
    resource = resource_entries[0]["resource"]
    logger.info(f"Checking {resource_type}.{field_name} value. Resource: {resource}")
    actual_value = resource.get(field_name)
    logger.info(f"actual value='{actual_value}'")
    assert actual_value == expected_bool, (
        f"Expected {resource_type}.{field_name} '{expected_bool}' but got '{actual_value}'"
    )


@then(parsers.parse('the "{resource_type}" resource has name field'))
def api_check_resource_type_name(fresponse, resource_type: str):
    """Verify {resource_type}.name exists and is a string."""
    response = fresponse.json()
    org_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource_type
    ]
    assert len(org_entries) > 0, f"No {resource_type} resource found"
    org = org_entries[0]["resource"]
    name = org.get("name")
    assert name is not None, f"{resource_type}.name field is missing"
    assert isinstance(name, str), (
        f"Expected name to be string but got {type(name).__name__}"
    )


@then(
    parsers.parse(
        'the "{resource_type}" resource identifier value matches ODS code pattern'
    )
)
def api_check_resource_type_identifier_value_pattern(fresponse, resource_type: str):
    """Verify {resource_type}.identifier[0].value matches ODS code pattern."""

    response = fresponse.json()
    org_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource_type
    ]
    assert len(org_entries) > 0, f"No {resource_type} resource found"
    org = org_entries[0]["resource"]
    identifier = org.get("identifier", [{}])[0]
    value = identifier.get("value")
    assert value is not None, f"{resource_type}.identifier.value is missing"
    pattern = r"^[A-Za-z0-9]{5,12}$"
    assert re.match(pattern, value), (
        f"ODS code '{value}' does not match pattern {pattern}"
    )


@then(parsers.parse("all Endpoint resources have status in {expected_values}"))
def api_check_all_endpoints_status(fresponse, expected_values: str):
    """Verify all Endpoint.status values are in the expected set."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > 0, "No Endpoint resources found"
    allowed_values = json.loads(expected_values)
    for entry in endpoint_entries:
        endpoint = entry["resource"]
        status = endpoint.get("status")
        assert status in allowed_values, (
            f"Endpoint status '{status}' not in allowed values {allowed_values}"
        )


@then("all Endpoint resources have connectionType with system and code")
def api_check_all_endpoints_connection_type(fresponse):
    """Verify all Endpoint.connectionType has system and code."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > 0, "No Endpoint resources found"
    for entry in endpoint_entries:
        endpoint = entry["resource"]
        conn_type = endpoint.get("connectionType", {})
        assert conn_type.get("system"), "Endpoint.connectionType.system is missing"
        assert conn_type.get("code"), "Endpoint.connectionType.code is missing"


@then("all Endpoint resources have managingOrganization reference")
def api_check_all_endpoints_managing_org(fresponse):
    """Verify all Endpoint.managingOrganization.reference exists."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > 0, "No Endpoint resources found"
    for entry in endpoint_entries:
        endpoint = entry["resource"]
        managing_org = endpoint.get("managingOrganization", {})
        ref = managing_org.get("reference")
        assert ref, "Endpoint.managingOrganization.reference is missing"


@then("all Endpoint resources have payloadType array")
def api_check_all_endpoints_payload_type(fresponse):
    """Verify all Endpoint.payloadType is a non-empty array."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > 0, "No Endpoint resources found"
    for entry in endpoint_entries:
        endpoint = entry["resource"]
        payload_type = endpoint.get("payloadType")
        assert isinstance(payload_type, list), "Endpoint.payloadType should be an array"
        assert len(payload_type) > 0, "Endpoint.payloadType array is empty"


@then("all Endpoint resources have payloadMimeType array")
def api_check_all_endpoints_payload_mime_type(fresponse):
    """Verify all Endpoint.payloadMimeType is a non-empty array."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > 0, "No Endpoint resources found"
    for entry in endpoint_entries:
        endpoint = entry["resource"]
        mime_types = endpoint.get("payloadMimeType")
        assert isinstance(mime_types, list), (
            "Endpoint.payloadMimeType should be an array"
        )
        assert len(mime_types) > 0, "Endpoint.payloadMimeType array is empty"


@then("all Endpoint resources have address field")
def api_check_all_endpoints_address(fresponse):
    """Verify all Endpoint.address exists."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > 0, "No Endpoint resources found"
    for entry in endpoint_entries:
        endpoint = entry["resource"]
        address = endpoint.get("address")
        assert address, "Endpoint.address is missing"


@then("all Endpoint managingOrganization references point to the parent Organization")
def api_check_endpoints_managing_org_reference(fresponse):
    """Verify Endpoint.managingOrganization.reference matches parent Organization."""
    response = fresponse.json()
    org_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Organization"
    ]
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(org_entries) > 0, "No Organization resource found"
    assert len(endpoint_entries) > 0, "No Endpoint resources found"
    org_id = org_entries[0]["resource"]["id"]
    for entry in endpoint_entries:
        endpoint = entry["resource"]
        ref = endpoint.get("managingOrganization", {}).get("reference", "")
        assert org_id in ref, (
            f"Endpoint managingOrganization reference '{ref}' does not contain Organization ID '{org_id}'"
        )


@then(
    parsers.parse("all Endpoint resources have extension {extension_name} as integer")
)
def api_check_endpoints_extension_integer(fresponse, extension_name: str):
    """Verify all Endpoints have the specified extension with integer value."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > 0, "No Endpoint resources found"
    extension_url_fragment = extension_name
    for entry in endpoint_entries:
        endpoint = entry["resource"]
        extensions = endpoint.get("extension", [])
        matching_ext = [
            ext for ext in extensions if extension_url_fragment in ext.get("url", "")
        ]
        assert len(matching_ext) > 0, (
            f"Extension '{extension_name}' not found in Endpoint"
        )
        value = matching_ext[0].get("valueInteger")
        assert isinstance(value, int), (
            f"Extension '{extension_name}' valueInteger should be int but got {type(value).__name__}"
        )


@then(
    parsers.parse("all Endpoint resources have extension {extension_name} as boolean")
)
def api_check_endpoints_extension_boolean(fresponse, extension_name: str):
    """Verify all Endpoints have the specified extension with boolean value."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > 0, "No Endpoint resources found"
    extension_url_fragment = extension_name
    for entry in endpoint_entries:
        endpoint = entry["resource"]
        extensions = endpoint.get("extension", [])
        matching_ext = [
            ext for ext in extensions if extension_url_fragment in ext.get("url", "")
        ]
        assert len(matching_ext) > 0, (
            f"Extension '{extension_name}' not found in Endpoint"
        )
        value = matching_ext[0].get("valueBoolean")
        assert isinstance(value, bool), (
            f"Extension '{extension_name}' valueBoolean should be bool but got {type(value).__name__}"
        )


@then(
    parsers.parse(
        "all Endpoint resources have extension {extension_name} with valid values"
    )
)
def api_check_endpoints_extension_valid_values(fresponse, extension_name: str):
    """Verify all Endpoints have the specified extension with valid enum values."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > 0, "No Endpoint resources found"
    extension_url_fragment = extension_name
    valid_values = ["primary-recipient", "copy-recipient"]
    for entry in endpoint_entries:
        endpoint = entry["resource"]
        extensions = endpoint.get("extension", [])
        matching_ext = [
            ext for ext in extensions if extension_url_fragment in ext.get("url", "")
        ]
        assert len(matching_ext) > 0, (
            f"Extension '{extension_name}' not found in Endpoint"
        )
        value = matching_ext[0].get("valueCode")
        assert value in valid_values, (
            f"Extension '{extension_name}' valueCode '{value}' not in {valid_values}"
        )


@then(
    parsers.parse('Endpoint {index:d} has "{field_name}" with value "{expected_value}"')
)
def api_check_endpoint_by_index_field_value(
    fresponse, index: int, field_name: str, expected_value: str
):
    """Verify a specific Endpoint field value by index (0-based)."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > index, (
        f"Endpoint index {index} not found. Only {len(endpoint_entries)} endpoints available."
    )
    endpoint = endpoint_entries[index]["resource"]
    actual_value = endpoint.get(field_name)
    assert actual_value == expected_value, (
        f"Endpoint[{index}].{field_name} expected '{expected_value}' but got '{actual_value}'"
    )


@then(
    parsers.parse(
        'Endpoint {index:d} has "{parent_field}.{child_field}" with value "{expected_value}"'
    )
)
def api_check_endpoint_by_index_nested_field_value(
    fresponse, index: int, parent_field: str, child_field: str, expected_value: str
):
    """Verify a nested field value in a specific Endpoint by index (0-based)."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > index, (
        f"Endpoint index {index} not found. Only {len(endpoint_entries)} endpoints available."
    )
    endpoint = endpoint_entries[index]["resource"]
    parent = endpoint.get(parent_field, {})
    actual_value = parent.get(child_field)
    assert actual_value == expected_value, (
        f"Endpoint[{index}].{parent_field}.{child_field} expected '{expected_value}' but got '{actual_value}'"
    )


@then(
    parsers.parse(
        'Endpoint {index:d} has extension "{extension_name}" with valueInteger {expected_value:d}'
    )
)
def api_check_endpoint_by_index_extension_integer(
    fresponse, index: int, extension_name: str, expected_value: int
):
    """Verify a specific Endpoint extension integer value by index (0-based)."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > index, (
        f"Endpoint index {index} not found. Only {len(endpoint_entries)} endpoints available."
    )
    endpoint = endpoint_entries[index]["resource"]
    extensions = endpoint.get("extension", [])
    matching_ext = [ext for ext in extensions if extension_name in ext.get("url", "")]
    assert len(matching_ext) > 0, (
        f"Extension '{extension_name}' not found in Endpoint[{index}]"
    )
    actual_value = matching_ext[0].get("valueInteger")
    assert actual_value == expected_value, (
        f"Endpoint[{index}] extension '{extension_name}' valueInteger expected {expected_value} but got {actual_value}"
    )


@then(
    parsers.parse(
        'Endpoint {index:d} has extension "{extension_name}" with valueBoolean {expected_value}'
    )
)
def api_check_endpoint_by_index_extension_boolean(
    fresponse, index: int, extension_name: str, expected_value: str
):
    """Verify a specific Endpoint extension boolean value by index (0-based)."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > index, (
        f"Endpoint index {index} not found. Only {len(endpoint_entries)} endpoints available."
    )
    endpoint = endpoint_entries[index]["resource"]
    extensions = endpoint.get("extension", [])
    matching_ext = [ext for ext in extensions if extension_name in ext.get("url", "")]
    assert len(matching_ext) > 0, (
        f"Extension '{extension_name}' not found in Endpoint[{index}]"
    )
    actual_value = matching_ext[0].get("valueBoolean")
    expected_bool = expected_value.lower() == "true"
    assert actual_value == expected_bool, (
        f"Endpoint[{index}] extension '{extension_name}' valueBoolean expected {expected_bool} but got {actual_value}"
    )


@then(
    parsers.parse(
        'Endpoint {index:d} has extension "{extension_name}" with valueCode "{expected_value}"'
    )
)
def api_check_endpoint_by_index_extension_code(
    fresponse, index: int, extension_name: str, expected_value: str
):
    """Verify a specific Endpoint extension code value by index (0-based)."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > index, (
        f"Endpoint index {index} not found. Only {len(endpoint_entries)} endpoints available."
    )
    endpoint = endpoint_entries[index]["resource"]
    extensions = endpoint.get("extension", [])
    matching_ext = [ext for ext in extensions if extension_name in ext.get("url", "")]
    assert len(matching_ext) > 0, (
        f"Extension '{extension_name}' not found in Endpoint[{index}]"
    )
    actual_value = matching_ext[0].get("valueCode")
    assert actual_value == expected_value, (
        f"Endpoint[{index}] extension '{extension_name}' valueCode expected '{expected_value}' but got '{actual_value}'"
    )


@then(
    parsers.parse(
        'Endpoint {index:d} has "{array_field}" containing "{expected_value}"'
    )
)
def api_check_endpoint_by_index_array_contains(
    fresponse, index: int, array_field: str, expected_value: str
):
    """Verify a specific Endpoint array field contains a value by index (0-based)."""
    response = fresponse.json()
    endpoint_entries = [
        e
        for e in response.get("entry", [])
        if e.get("resource", {}).get("resourceType") == "Endpoint"
    ]
    assert len(endpoint_entries) > index, (
        f"Endpoint index {index} not found. Only {len(endpoint_entries)} endpoints available."
    )
    endpoint = endpoint_entries[index]["resource"]
    array_values = endpoint.get(array_field, [])
    assert expected_value in array_values, (
        f"Endpoint[{index}].{array_field} does not contain '{expected_value}'. Found: {array_values}"
    )
