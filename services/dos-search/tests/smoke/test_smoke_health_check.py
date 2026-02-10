"""
Smoke Tests: Health Check

Tests the health check endpoint to validate service availability and basic functionality.
These tests should run frequently (every 5 minutes) to detect service issues quickly.
"""

import requests
from requests.exceptions import ConnectionError, Timeout


class TestHealthCheckSmoke:
    """Smoke tests for the health check endpoint"""

    def test_health_endpoint_returns_200(self, base_url, timeout):
        """
        CRITICAL: Health check endpoint must return 200 OK

        This test validates that the service is running and responding.
        Should run every 5 minutes in production.
        """
        # Arrange
        health_url = f"{base_url}/health"

        # Act
        try:
            response = requests.get(health_url, timeout=timeout)
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"Health check endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 200
        ), f"Health check failed with status {response.status_code}"

    def test_health_endpoint_response_time(self, base_url, timeout):
        """
        Health check should respond within acceptable time

        Validates that the service responds quickly (< 2 seconds).
        Slow responses may indicate resource constraints.
        """
        # Arrange
        health_url = f"{base_url}/health"
        max_response_time = 2.0  # seconds

        # Act
        try:
            response = requests.get(health_url, timeout=timeout)
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"Health check endpoint unreachable: {e}")

        # Assert
        assert response.elapsed.total_seconds() < max_response_time, (
            f"Health check took {response.elapsed.total_seconds():.2f}s, "
            f"expected < {max_response_time}s"
        )

    def test_health_endpoint_returns_json(self, base_url, timeout):
        """
        Health check should return valid JSON response

        Validates the response format is correct.
        """
        # Arrange
        health_url = f"{base_url}/health"

        # Act
        try:
            response = requests.get(health_url, timeout=timeout)
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"Health check endpoint unreachable: {e}")

        # Assert
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "json" in content_type.lower(), f"Expected JSON response, got {content_type}"

        # Validate it's parseable JSON
        try:
            response.json()
        except ValueError:
            pytest.fail("Health check response is not valid JSON")

    def test_health_endpoint_contains_status(self, base_url, timeout):
        """
        Health check response should contain status information

        Validates that the health check provides meaningful status data.
        """
        # Arrange
        health_url = f"{base_url}/health"

        # Act
        try:
            response = requests.get(health_url, timeout=timeout)
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"Health check endpoint unreachable: {e}")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Check for common health check fields
        assert isinstance(data, dict), "Health check should return a JSON object"
        # Note: Adjust assertions based on actual health check response structure

    def test_health_endpoint_no_authentication_required(self, base_url, timeout):
        """
        Health check should not require authentication

        Validates that health checks can be performed without credentials.
        This allows monitoring systems to check service status.
        """
        # Arrange
        health_url = f"{base_url}/health"
        headers = {}  # No authorization header

        # Act
        try:
            response = requests.get(health_url, headers=headers, timeout=timeout)
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"Health check endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 200
        ), "Health check should not require authentication"


class TestHealthCheckResilience:
    """Tests for health check endpoint resilience"""

    def test_health_check_handles_concurrent_requests(self, base_url, timeout):
        """
        Health check should handle multiple concurrent requests

        Validates that the health endpoint can handle load.
        """
        # Arrange
        health_url = f"{base_url}/health"
        num_requests = 5

        # Act
        import concurrent.futures

        def make_request():
            return requests.get(health_url, timeout=timeout)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
                futures = [executor.submit(make_request) for _ in range(num_requests)]
                responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"Health check endpoint failed under concurrent load: {e}")

        # Assert
        for response in responses:
            assert (
                response.status_code == 200
            ), f"Concurrent health check failed with status {response.status_code}"

    def test_health_check_with_invalid_method(self, base_url, timeout):
        """
        Health check should reject non-GET methods gracefully

        Validates proper handling of invalid HTTP methods.
        """
        # Arrange
        health_url = f"{base_url}/health"

        # Act
        try:
            response = requests.post(health_url, timeout=timeout)
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"Health check endpoint unreachable: {e}")

        # Assert
        assert response.status_code in [
            405,
            400,
        ], f"Expected 405 or 400 for POST, got {response.status_code}"


# Import pytest at the end to avoid import errors if not installed
import pytest
