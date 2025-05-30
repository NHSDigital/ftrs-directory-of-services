import os
import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from pipeline.utilities import (
    get_base_crud_api_url,
    get_signed_request_headers,
    make_request,
)


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "dev",
        "WORKSPACE": "test_workspace",
    },
)
@patch("pipeline.utilities.get_parameter")
def test_get_base_crud_api_url(
    get_parameter_mock: MagicMock,
) -> None:
    get_base_crud_api_url.cache_clear()

    get_parameter_mock.return_value = "https://api.example.com"
    expected_url = "https://api.example.com"

    url = get_base_crud_api_url()

    assert url == expected_url

    assert get_parameter_mock.call_count == 1
    get_parameter_mock.assert_called_once_with(
        name="/ftrs-dos-dev-crud-apis-test_workspace/endpoint"
    )


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "dev", "WORKSPACE": ""},
)
@patch("pipeline.utilities.get_parameter")
def test_get_base_crud_api_url_no_workspace(
    get_parameter_mock: MagicMock,
) -> None:
    get_base_crud_api_url.cache_clear()

    get_parameter_mock.return_value = "https://api.example.com"
    expected_url = "https://api.example.com"

    url = get_base_crud_api_url()

    assert url == expected_url

    assert get_parameter_mock.call_count == 1
    get_parameter_mock.assert_called_once_with(name="/ftrs-dos-dev-crud-apis/endpoint")


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "local",
        "WORKSPACE": "",
        "LOCAL_CRUD_API_URL": "https://localhost:8001/",
    },
)
@patch("pipeline.utilities.get_parameter")
def test_get_base_crud_api_url_local_workspace(
    get_parameter_mock: MagicMock,
) -> None:
    get_base_crud_api_url.cache_clear()
    expected_url = "https://localhost:8001/"

    url = get_base_crud_api_url()

    assert url == expected_url
    assert get_parameter_mock.call_count == 0


def test_get_signed_request_headers() -> None:
    """
    Test the get_signed_request_headers function.
    """
    method = "GET"
    url = "https://api.example.com/resource"
    host = "api.example.com"
    region = "eu-west-2"

    headers = get_signed_request_headers(method, url, host, region)

    assert isinstance(headers, dict)
    assert "Authorization" in headers
    assert "X-Amz-Date" in headers
    assert "X-Amz-Security-Token" in headers
    assert headers["Host"] == host


@patch("pipeline.utilities.requests.get")
def test_make_request_success(mock_get: MagicMock) -> None:
    """
    Test the make_request function for a successful request.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    url = "https://api.example.com/resource"
    result = make_request(url)

    assert result == {"key": "value"}
    mock_get.assert_called_once_with(url, params=None, timeout=20, headers={})


@patch("pipeline.utilities.requests.get")
def test_make_request_with_params(mock_get: MagicMock) -> None:
    """
    Test the make_request function with parameters.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    url = "https://api.example.com/resource"
    params = {"param1": "value1", "param2": "value2"}
    result = make_request(url, params=params)

    assert result == {"key": "value"}
    mock_get.assert_called_once_with(url, params=params, timeout=20, headers={})


@patch("pipeline.utilities.requests.get")
@patch("pipeline.utilities.get_signed_request_headers")
def test_make_request_signed_request(
    mock_get_headers: MagicMock,
    mock_get: MagicMock,
) -> None:
    """
    Test the make_request function with signed request.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    mock_get_headers.return_value = {
        "Authorization": "MockedAuthorization",
        "X-Amz-Date": "MockedDate",
        "X-Amz-Security-Token": "MockedToken",
        "Host": "api.example.com",
    }

    url = "https://api.example.com/resource"
    result = make_request(url, sign=True)

    assert result == {"key": "value"}
    mock_get.assert_called_once_with(
        url, params=None, timeout=20, headers=mock_get.call_args[1]["headers"]
    )

    mock_get_headers.assert_called_once_with(
        method="GET", url=url, host="api.example.com", region="eu-west-2"
    )


@patch("pipeline.utilities.requests.get")
def test_make_request_http_error(mock_get: MagicMock) -> None:
    """
    Test the make_request function for an HTTP error.
    """
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Not Found"
    )
    mock_get.return_value = mock_response

    url = "https://api.example.com/resource"

    with pytest.raises(requests.exceptions.HTTPError, match="404 Not Found"):
        make_request(url)

    mock_get.assert_called_once_with(url, params=None, timeout=20, headers={})


@patch("pipeline.utilities.requests.get")
def test_make_request_request_exception(mock_get: MagicMock) -> None:
    """
    Test the make_request function for a request exception.
    """
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    url = "https://api.example.com/resource"

    with pytest.raises(requests.exceptions.RequestException, match="Connection error"):
        make_request(url)

    mock_get.assert_called_once_with(url, params=None, timeout=20, headers={})
