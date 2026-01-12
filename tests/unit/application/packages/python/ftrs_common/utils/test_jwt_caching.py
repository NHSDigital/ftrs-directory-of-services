"""Test JWT authentication with caching functionality."""

import json
import os
import pytest
from time import time
from unittest.mock import patch, MagicMock, mock_open

from application.packages.python.ftrs_common.utils.jwt_auth import JWTAuthenticator


class TestJWTAuthenticatorCaching:
    """Test JWT token caching functionality."""

    @pytest.fixture
    def mock_environment(self) -> None:
        """Set up mock environment variables."""
        env_vars = {
            "LOCAL_API_KEY": "test-api-key",
            "LOCAL_PRIVATE_KEY": "FAKE_TEST_PRIVATE_KEY_FOR_MOCKING_ONLY",
            "LOCAL_KID": "test-kid",
            "LOCAL_TOKEN_URL": "https://test-token-url.com/token",
        }
        with patch.dict(os.environ, env_vars):
            yield

    @pytest.fixture
    def jwt_authenticator(self, mock_environment) -> JWTAuthenticator:
        """Create a JWT authenticator instance for testing."""
        return JWTAuthenticator(environment="local")

    @patch("application.packages.python.ftrs_common.utils.jwt_auth.requests.post")
    def test_bearer_token_caching_first_request(
        self, mock_post: MagicMock, jwt_authenticator: JWTAuthenticator
    ) -> None:
        """Test that first token request generates new token and caches it."""
        # Mock successful token response
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test-bearer-token"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Initial state - no cached token
        assert jwt_authenticator._cached_token is None
        assert jwt_authenticator._token_expires_at is None

        # First request should generate new token
        token = jwt_authenticator.get_bearer_token()

        assert token == "test-bearer-token"
        assert jwt_authenticator._cached_token == "test-bearer-token"
        assert jwt_authenticator._token_expires_at is not None
        assert mock_post.call_count == 1

    @patch("application.packages.python.ftrs_common.utils.jwt_auth.requests.post")
    def test_bearer_token_caching_subsequent_request(
        self, mock_post: MagicMock, jwt_authenticator: JWTAuthenticator
    ) -> None:
        """Test that subsequent requests use cached token."""
        # Mock successful token response
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test-bearer-token"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # First request
        token1 = jwt_authenticator.get_bearer_token()
        assert mock_post.call_count == 1

        # Second request should use cached token
        token2 = jwt_authenticator.get_bearer_token()

        assert token1 == token2
        assert token2 == "test-bearer-token"
        # Should not make another HTTP request
        assert mock_post.call_count == 1

    @patch("application.packages.python.ftrs_common.utils.jwt_auth.requests.post")
    @patch("application.packages.python.ftrs_common.utils.jwt_auth.time")
    def test_bearer_token_cache_expiry(
        self, mock_time: MagicMock, mock_post: MagicMock, jwt_authenticator: JWTAuthenticator
    ) -> None:
        """Test that expired cached token triggers new request."""
        # Mock time progression
        mock_time.return_value = 1000.0  # Start time

        # Mock successful token responses
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {"access_token": "token-1"}
        mock_response1.raise_for_status.return_value = None

        mock_response2 = MagicMock()
        mock_response2.json.return_value = {"access_token": "token-2"}
        mock_response2.raise_for_status.return_value = None

        mock_post.side_effect = [mock_response1, mock_response2]

        # First request at time 1000
        token1 = jwt_authenticator.get_bearer_token()
        assert token1 == "token-1"
        assert mock_post.call_count == 1

        # Move time forward but within cache period (< 300 seconds)
        mock_time.return_value = 1200.0  # 200 seconds later
        token2 = jwt_authenticator.get_bearer_token()
        assert token2 == "token-1"  # Should use cached token
        assert mock_post.call_count == 1

        # Move time forward beyond cache expiry (> 300 seconds)
        mock_time.return_value = 1400.0  # 400 seconds later
        token3 = jwt_authenticator.get_bearer_token()
        assert token3 == "token-2"  # Should get new token
        assert mock_post.call_count == 2

    @patch("application.packages.python.ftrs_common.utils.jwt_auth.requests.post")
    def test_bearer_token_caching_with_auth_headers(
        self, mock_post: MagicMock, jwt_authenticator: JWTAuthenticator
    ) -> None:
        """Test that auth headers method also benefits from caching."""
        # Mock successful token response
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test-bearer-token"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Multiple calls to get_auth_headers should reuse cached token
        headers1 = jwt_authenticator.get_auth_headers()
        headers2 = jwt_authenticator.get_auth_headers()

        assert headers1 == {"Authorization": "Bearer test-bearer-token"}
        assert headers2 == {"Authorization": "Bearer test-bearer-token"}
        # Should only make one HTTP request due to caching
        assert mock_post.call_count == 1

    @patch("application.packages.python.ftrs_common.utils.jwt_auth.requests.post")
    def test_bearer_token_caching_after_error_recovery(
        self, mock_post: MagicMock, jwt_authenticator: JWTAuthenticator
    ) -> None:
        """Test caching behavior after error and recovery."""
        # First request fails
        mock_post.side_effect = Exception("Network error")

        with pytest.raises(Exception):
            jwt_authenticator.get_bearer_token()

        # Token should not be cached after failure
        assert jwt_authenticator._cached_token is None

        # Second request succeeds
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "recovery-token"}
        mock_response.raise_for_status.return_value = None
        mock_post.side_effect = None
        mock_post.return_value = mock_response

        token = jwt_authenticator.get_bearer_token()
        assert token == "recovery-token"
        assert jwt_authenticator._cached_token == "recovery-token"

    def test_cache_isolation_between_instances(self, mock_environment) -> None:
        """Test that different instances have separate caches."""
        auth1 = JWTAuthenticator(environment="local")
        auth2 = JWTAuthenticator(environment="local")

        # Set cache on first instance
        auth1._cached_token = "token-1"
        auth1._token_expires_at = time() + 300

        # Second instance should have empty cache
        assert auth2._cached_token is None
        assert auth2._token_expires_at is None

        # Set cache on second instance
        auth2._cached_token = "token-2"
        auth2._token_expires_at = time() + 300

        # Both instances should maintain their own caches
        assert auth1._cached_token == "token-1"
        assert auth2._cached_token == "token-2"
