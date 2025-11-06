from http import HTTPStatus

import pytest
import requests

from tests.constants import ENDPOINTS


@pytest.mark.smoketest
class TestStatusEndpoints:
    def test_ping_endpoint(self, service_url: str) -> None:
        """
        Send a request to _ping endpoint to test health of proxy.
        """
        response = requests.get(f"{service_url}{ENDPOINTS['health']}")
        assert response.status_code == HTTPStatus.OK, (
            f"UNEXPECTED RESPONSE: Actual response status code = {response.status_code}"
        )

    def test_status_is_secured(self, service_url: str) -> None:
        """
        Send an unauthenticated request to status to check secured
        """
        resp = requests.get(f"{service_url}{ENDPOINTS['status']}")
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_endpoint_is_secured(self, service_url: str) -> None:
        """
        Send an unauthenticated request to endpoint to check secured
        """
        url = (
            f"{service_url}{ENDPOINTS['organization']}/0000-0000-0000-0000-00000000000a"
        )
        resp = requests.put(url)
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_endpoint_api_key_valid(self, service_url: str, api_key: str) -> None:
        """
        Send an authenticated request to endpoint to check API key
        """
        url = (
            f"{service_url}{ENDPOINTS['organization']}/0000-0000-0000-0000-00000000000a"
        )
        headers = {"apikey": api_key}
        resp = requests.put(url, headers=headers)
        assert resp.status_code != HTTPStatus.UNAUTHORIZED
