from http import HTTPStatus

from ftrs_common.fhir.operation_outcome_status_mapper import STATUS_CODE_MAP


def test_status_code_map_contains_expected_keys() -> None:
    expected_keys = [
        "not-found",
        "invalid",
        "exception",
        "forbidden",
        "processing",
        "duplicate",
        "structure",
        "security",
        "not-supported",
        "business-rule",
        "informational",
    ]
    for key in expected_keys:
        assert key in STATUS_CODE_MAP


def test_status_code_map_values() -> None:
    assert STATUS_CODE_MAP["not-found"] == HTTPStatus.NOT_FOUND
    assert STATUS_CODE_MAP["invalid"] == HTTPStatus.UNPROCESSABLE_ENTITY
    assert STATUS_CODE_MAP["exception"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert STATUS_CODE_MAP["forbidden"] == HTTPStatus.FORBIDDEN
    assert STATUS_CODE_MAP["processing"] == HTTPStatus.ACCEPTED
    assert STATUS_CODE_MAP["duplicate"] == HTTPStatus.CONFLICT
    assert STATUS_CODE_MAP["structure"] == HTTPStatus.BAD_REQUEST
    assert STATUS_CODE_MAP["security"] == HTTPStatus.UNAUTHORIZED
    assert STATUS_CODE_MAP["not-supported"] == HTTPStatus.METHOD_NOT_ALLOWED
    assert STATUS_CODE_MAP["business-rule"] == HTTPStatus.UNPROCESSABLE_ENTITY
    assert STATUS_CODE_MAP["informational"] == HTTPStatus.OK


def test_status_code_map_no_extra_keys() -> None:
    allowed_keys = {
        "not-found",
        "invalid",
        "exception",
        "forbidden",
        "processing",
        "duplicate",
        "structure",
        "security",
        "not-supported",
        "business-rule",
        "informational",
    }
    assert set(STATUS_CODE_MAP.keys()) == allowed_keys


def test_status_code_map_values_validity() -> None:
    valid_status_codes = set(s.value for s in HTTPStatus)
    for status_code in STATUS_CODE_MAP.values():
        assert status_code in valid_status_codes
