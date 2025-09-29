from ftrs_common.utils.correlation_id import (
    CORRELATION_ID_HEADER,
    add_correlation_id_header,
    correlation_id_context,
    ensure_correlation_id,
    extract_correlation_id,
    generate_correlation_id,
    get_correlation_id,
    set_correlation_id,
)


def test_generate_correlation_id_returns_string() -> None:
    """Test that generate_correlation_id returns a valid string."""
    correlation_id = generate_correlation_id()
    assert isinstance(correlation_id, str)


def test_set_and_get_correlation_id() -> None:
    """Test that set_correlation_id sets the correlation ID and get_correlation_id retrieves it."""
    test_id = "test-correlation-id"
    set_correlation_id(test_id)
    assert get_correlation_id() == test_id


def test_set_correlation_id_ignores_none() -> None:
    """Test that set_correlation_id doesn't change the context when None is provided."""
    test_id = "test-correlation-id"
    set_correlation_id(test_id)
    set_correlation_id(None)
    assert get_correlation_id() == test_id


def test_correlation_id_context_sets_and_resets_id() -> None:
    """Test that correlation_id_context sets the ID within the context and resets after."""
    original_id = "original-id"
    context_id = "context-id"

    set_correlation_id(original_id)

    with correlation_id_context(context_id):
        assert get_correlation_id() == context_id

    assert get_correlation_id() == original_id


def test_correlation_id_context_without_id() -> None:
    """Test that correlation_id_context works even if no ID is provided."""
    original_id = "original-id"
    set_correlation_id(original_id)

    with correlation_id_context():
        assert get_correlation_id() == original_id

    assert get_correlation_id() == original_id


def test_ensure_correlation_id_uses_provided_id() -> None:
    """Test that ensure_correlation_id uses the provided ID."""
    provided_id = "provided-id"
    result = ensure_correlation_id(provided_id)

    assert result == provided_id
    assert get_correlation_id() == provided_id


def test_ensure_correlation_id_uses_context_id() -> None:
    """Test that ensure_correlation_id uses the context ID if no ID is provided."""
    context_id = "context-id"
    set_correlation_id(context_id)

    result = ensure_correlation_id()

    assert result == context_id
    assert get_correlation_id() == context_id


def test_ensure_correlation_id_generates_new_id() -> None:
    """Test that ensure_correlation_id generates a new ID if none is provided or in context."""
    set_correlation_id(None)

    result = ensure_correlation_id()

    assert result is not None
    assert get_correlation_id() == result


class MockRequest:
    """Mock request class that implements the RequestLike protocol."""

    def __init__(self, headers: dict) -> None:
        self.headers = headers


def test_extract_correlation_id_from_headers() -> None:
    """Test that extract_correlation_id extracts the ID from request headers."""
    header_id = "header-id"
    request = MockRequest({CORRELATION_ID_HEADER: header_id})

    result = extract_correlation_id(request)

    assert result == header_id
    assert get_correlation_id() == header_id


def test_extract_correlation_id_generates_id_if_not_in_headers() -> None:
    """Test that extract_correlation_id generates an ID if not in headers."""
    request = MockRequest({})

    result = extract_correlation_id(request)

    assert result is not None
    assert get_correlation_id() == result


class MockResponse:
    """Mock response class that implements the ResponseLike protocol."""

    def __init__(self) -> None:
        self.headers = {}


def test_add_correlation_id_header_uses_provided_id() -> None:
    """Test that add_correlation_id_header uses the provided ID."""
    response = MockResponse()
    header_id = "header-id"

    result = add_correlation_id_header(response, header_id)

    assert result is response
    assert response.headers[CORRELATION_ID_HEADER] == header_id


def test_add_correlation_id_header_generates_id() -> None:
    """Test that add_correlation_id_header generates an ID if none is provided or in context."""
    response = MockResponse()
    set_correlation_id(None)

    result = add_correlation_id_header(response)

    assert result is response
    assert CORRELATION_ID_HEADER in response.headers


def test_add_correlation_id_header_handles_non_header_object() -> None:
    """Test that add_correlation_id_header can handle objects without headers attribute."""

    class ObjectWithoutHeaders:
        pass

    obj = ObjectWithoutHeaders()
    header_id = "header-id"

    result = add_correlation_id_header(obj, header_id)

    assert result is obj
