from http import HTTPStatus

import pytest
import requests

from tests.unit.constants import ENDPOINTS


@pytest.mark.smoketest
class TestStatusEndpoints:
    def test_ping_endpoint(self, service_url: str) -> None:
        """
        Send a request to _ping endpoint to test health of proxy.
        """
        response = requests.get(f"{service_url}{ENDPOINTS['ping']}")
        assert response.status_code == HTTPStatus.OK, (
            f"UNEXPECTED RESPONSE: Actual response status code = {response.status_code}"
        )

    def test_status_is_secured(self, service_url: str) -> None:
        """
        Send an unauthenticated request to status to check secured
        """
        resp = requests.get(f"{service_url}{ENDPOINTS['status']}")
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_status_endpoint(self, service_url: str, api_key: str) -> None:
        response = requests.get(
            f"{service_url}{ENDPOINTS['status']}", headers={"apikey": api_key}
        )
        assert response.status_code == HTTPStatus.OK, (
            f"UNEXPECTED RESPONSE: Actual response status code = {response.status_code}"
        )
        data = response.json()
        # Check top-level status
        assert data.get("status") == "pass", (
            "UNEXPECTED RESPONSE: Health check failed: $.status != 'pass'"
        )
        # Check all healthcheckService:status entries
        checks = data.get("checks", {}).get("healthcheckService:status", [])
        assert isinstance(checks, list), (
            "UNEXPECTED RESPONSE: "
            "Expected checks['healthcheckService:status'] to be a list"
        )
        for check in checks:
            assert check.get("status") == "pass", (
                "UNEXPECTED RESPONSE: "
                "Health check failed: $.checks['healthcheckService:status'][*].status != 'pass'"
            )
