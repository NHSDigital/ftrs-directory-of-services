import os
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
from botocore.credentials import Credentials
from requests_mock import Mocker as RequestsMock

from pipeline.utilities import (
    get_base_crud_api_url,
    get_signed_request_headers,
    make_request,
)


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "dev",
        "WORKSPACE": "test-workspace",
    },
)
def test_get_base_crud_api_url(
    mock_get_parameter: MagicMock,
) -> None:
    get_base_crud_api_url.cache_clear()
    expected_url = "http://test-crud-api"
    url = get_base_crud_api_url()

    assert url == expected_url

    assert mock_get_parameter.call_count == 1
    mock_get_parameter.assert_called_once_with(
        name="/ftrs-dos-dev-crud-apis-test-workspace/endpoint"
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


@patch("pipeline.utilities.boto3.Session")
def test_get_signed_request_headers(session_mock: MagicMock) -> None:
    """
    Test the get_signed_request_headers function.
    """
    session_mock.return_value.get_credentials.return_value = Credentials(
        access_key="mock_access_key",
        secret_key="mock_secret_key",
        token="mock_token",
    )

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


def test_make_request_success(requests_mock: RequestsMock) -> None:
    """
    Test the make_request function for a successful request.
    """
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    result = make_request(url)

    assert result.json() == {"key": "value"}

    assert mock_call.last_request.url == url
    assert mock_call.last_request.method == "GET"
    assert mock_call.last_request.headers == {
        "User-Agent": "python-requests/2.32.3",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }


@patch("pipeline.utilities.boto3.Session")
def test_make_request_with_params(
    session_mock: MagicMock,
    requests_mock: RequestsMock,
) -> None:
    """
    Test the make_request function with parameters.
    """
    session_mock.return_value.get_credentials.return_value = Credentials(
        access_key="mock_access_key",
        secret_key="mock_secret_key",
        token="mock_token",
    )

    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    url = "https://api.example.com/resource"
    params = {"param1": "value1", "param2": "value2"}
    result = make_request(url, params=params)

    assert result.status_code == HTTPStatus.OK
    assert result.json() == {"key": "value"}

    assert (
        mock_call.last_request.url
        == "https://api.example.com/resource?param1=value1&param2=value2"
    )
    assert mock_call.last_request.method == "GET"
    assert mock_call.last_request.headers == {
        "User-Agent": "python-requests/2.32.3",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }
    assert mock_call.last_request.qs == {"param1": ["value1"], "param2": ["value2"]}


@patch("pipeline.utilities.get_signed_request_headers")
def test_make_request_signed_request(
    mock_get_headers: MagicMock,
    requests_mock: RequestsMock,
) -> None:
    """
    Test the make_request function with signed request.
    """
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        json={"key": "value"},
        status_code=HTTPStatus.OK,
    )

    mock_get_headers.return_value = {
        "Authorization": "MockedAuthorization",
        "X-Amz-Date": "MockedDate",
        "X-Amz-Security-Token": "MockedToken",
        "Host": "api.example.com",
    }

    url = "https://api.example.com/resource"
    result = make_request(url, sign=True)

    assert result.status_code == HTTPStatus.OK
    assert result.json() == {"key": "value"}

    mock_get_headers.assert_called_once_with(
        method="GET", url=url, host="api.example.com", region="eu-west-2"
    )

    assert mock_call.last_request.url == url
    assert mock_call.last_request.method == "GET"
    assert mock_call.last_request.headers == {
        "User-Agent": "python-requests/2.32.3",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Authorization": "MockedAuthorization",
        "X-Amz-Date": "MockedDate",
        "X-Amz-Security-Token": "MockedToken",
        "Host": "api.example.com",
    }


def test_make_request_http_error(requests_mock: RequestsMock) -> None:
    """
    Test the make_request function for an HTTP error.
    """
    mock_call = requests_mock.get(
        "https://api.example.com/resource",
        status_code=HTTPStatus.NOT_FOUND,
        json={"error": "Resource not found"},
    )

    url = "https://api.example.com/resource"

    with pytest.raises(
        requests.exceptions.HTTPError,
        match="404 Client Error: None for url: https://api.example.com/resource",
    ):
        make_request(url)

    assert mock_call.last_request.url == url
    assert mock_call.last_request.method == "GET"


def test_make_request_request_exception(requests_mock: RequestsMock) -> None:
    """
    Test the make_request function for a request exception.
    """
    mock_get = requests_mock.get(
        "https://api.example.com/resource",
        exc=requests.exceptions.RequestException("Connection error"),
    )

    url = "https://api.example.com/resource"

    with pytest.raises(requests.exceptions.RequestException, match="Connection error"):
        make_request(url)

    assert mock_get.last_request.url == url
    assert mock_get.last_request.method == "GET"
