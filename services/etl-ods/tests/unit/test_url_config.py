"""Tests for URL configuration utilities."""

import os
from unittest.mock import patch

import pytest

from common.url_config import get_base_apim_api_url, get_base_ods_terminology_api_url


class TestUrlConfig:
    """Test cases for URL configuration functions."""

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "dev",
            "APIM_URL": "non-local-api-url",
        },
    )
    def test_get_base_apim_api_url_non_local(self) -> None:
        """Test get_base_apim_api_url returns APIM_URL for non-local environment."""
        # Clear the cache to ensure the patched environment variables are used
        get_base_apim_api_url.cache_clear()
        result = get_base_apim_api_url()
        assert result == "non-local-api-url"

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "local",
            "LOCAL_APIM_API_URL": "http://test-apim-api",
        },
    )
    def test_get_base_apim_api_url_local(self) -> None:
        """Test get_base_apim_api_url returns LOCAL_APIM_API_URL for local environment."""
        get_base_apim_api_url.cache_clear()
        result = get_base_apim_api_url()
        assert result == "http://test-apim-api"

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "dev",
            "ODS_URL": "non-local-ods-api-url",
        },
    )
    def test_get_base_ods_terminology_api_url_non_local(self) -> None:
        """Test get_base_ods_terminology_api_url returns ODS_URL for non-local environment."""
        get_base_ods_terminology_api_url.cache_clear()
        result = get_base_ods_terminology_api_url()
        assert result == "non-local-ods-api-url"

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "local",
            "LOCAL_ODS_URL": "http://local-ods-api",
        },
    )
    def test_get_base_ods_terminology_api_url_local_with_env_var(self) -> None:
        """Test get_base_ods_terminology_api_url returns LOCAL_ODS_URL for local environment when set."""
        get_base_ods_terminology_api_url.cache_clear()
        result = get_base_ods_terminology_api_url()
        assert result == "http://local-ods-api"

    @patch.dict(os.environ, {"ENVIRONMENT": "local"}, clear=True)
    def test_get_base_ods_terminology_api_url_local_default(self) -> None:
        """Test get_base_ods_terminology_api_url returns default URL for local environment when LOCAL_ODS_URL not set."""
        get_base_ods_terminology_api_url.cache_clear()
        result = get_base_ods_terminology_api_url()
        assert (
            result
            == "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
        )

    @patch.dict(os.environ, {"ENVIRONMENT": "dev"}, clear=True)
    def test_get_base_ods_terminology_api_url_missing_ods_url(self) -> None:
        """Test get_base_ods_terminology_api_url raises KeyError when ODS_URL is not set in non-local environment."""
        get_base_ods_terminology_api_url.cache_clear()
        with pytest.raises(KeyError) as exc_info:
            get_base_ods_terminology_api_url()
        assert str(exc_info.value) == "'ODS_URL environment variable is not set'"
