from ftrs_common.utils.request_id import (
    REQUEST_ID_HEADER,
    add_request_id_header,
    fetch_or_set_request_id,
    generate_request_id,
    get_request_id,
    request_id_context,
    set_request_id,
)


def test_generate_request_id_returns_string() -> None:
    """Test that generate_request_id returns a valid string."""
    request_id = generate_request_id()
    assert isinstance(request_id, str)
    assert len(request_id) > 0


def test_set_and_get_request_id() -> None:
    """Test that set_request_id sets the request ID and get_request_id retrieves it."""
    test_id = "test-request-id"
    set_request_id(test_id)
    assert get_request_id() == test_id


def test_set_request_id_ignores_none() -> None:
    """Test that set_request_id doesn't change the context when None is provided."""
    original_id = "original-id"
    set_request_id(original_id)
    set_request_id(None)
    assert get_request_id() == original_id


def test_request_id_context_sets_and_resets_id() -> None:
    """Test that request_id_context sets the ID within the context and resets after."""
    original_id = "original-id"
    context_id = "context-id"

    set_request_id(original_id)

    with request_id_context(context_id):
        assert get_request_id() == context_id

    assert get_request_id() == original_id


def test_request_id_context_without_id() -> None:
    """Test that request_id_context works even if no ID is provided."""
    original_id = "original-id"
    set_request_id(original_id)

    with request_id_context():
        assert get_request_id() == original_id

    assert get_request_id() == original_id


def test_fetch_or_set_request_id_uses_header_id() -> None:
    """Test that fetch_or_set_request_id prioritizes header ID."""
    header_id = "header-id"
    context_id = "context-id"

    result = fetch_or_set_request_id(context_id=context_id, header_id=header_id)

    assert result == header_id
    assert get_request_id() == header_id


def test_fetch_or_set_request_id_uses_context_id() -> None:
    """Test that fetch_or_set_request_id uses context ID when header ID is not provided."""
    context_id = "context-id"

    result = fetch_or_set_request_id(context_id=context_id)

    assert result == context_id
    assert get_request_id() == context_id


def test_fetch_or_set_request_id_uses_existing_context() -> None:
    """Test that fetch_or_set_request_id uses the existing context ID if none is provided."""
    existing_id = "existing-id"
    set_request_id(existing_id)

    result = fetch_or_set_request_id()

    assert result == existing_id
    assert get_request_id() == existing_id


def test_fetch_or_set_request_id_generates_new_id() -> None:
    """Test that fetch_or_set_request_id generates a new ID if none is provided or in context."""
    set_request_id(None)

    result = fetch_or_set_request_id()

    assert result is not None
    assert get_request_id() == result


class MockResponse:
    """Mock response class that implements the ResponseLike protocol."""

    def __init__(self) -> None:
        self.headers = {}


def test_add_request_id_header_uses_provided_id() -> None:
    """Test that add_request_id_header uses the provided ID."""
    response = MockResponse()
    request_id = "test-request-id"

    result = add_request_id_header(response, request_id)

    assert result is response
    assert response.headers[REQUEST_ID_HEADER] == request_id


def test_add_request_id_header_generates_id() -> None:
    """Test that add_request_id_header generates an ID if none is provided or in context."""
    response = MockResponse()
    set_request_id(None)

    result = add_request_id_header(response)

    assert result is response
    assert REQUEST_ID_HEADER in response.headers


def test_add_request_id_header_handles_non_header_object() -> None:
    """Test that add_request_id_header can handle objects without headers attribute."""

    class ObjectWithoutHeaders:
        pass

    obj = ObjectWithoutHeaders()
    request_id = "test-id"

    result = add_request_id_header(obj, request_id)

    assert result is obj
