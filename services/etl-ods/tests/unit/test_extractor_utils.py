import os
from unittest.mock import MagicMock, patch

import pytest
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from extractor.utils import is_mock_testing_mode, is_ods_terminology_request


class TestIsOdsTerminologyRequest:
    def test_ods_terminology_url_returns_true(self) -> None:
        """Test that URLs containing 'organisation-data-terminology-api' return True."""
        url = "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
        assert is_ods_terminology_request(url) is True

    def test_non_ods_terminology_url_returns_false(self) -> None:
        """Test that URLs not containing 'organisation-data-terminology-api' return False."""
        url = "https://api.service.nhs.uk/some-other-api/fhir/Organization"
        assert is_ods_terminology_request(url) is False

    def test_partial_match_returns_false(self) -> None:
        """Test that partial matches don't incorrectly return True."""
        url = "https://api.service.nhs.uk/organisation-data-api/fhir/Organization"
        assert is_ods_terminology_request(url) is False

    def test_empty_url_returns_false(self) -> None:
        """Test that empty URL returns False."""
        assert is_ods_terminology_request("") is False

    def test_case_sensitive_check(self) -> None:
        """Test that the check is case sensitive."""
        url = "https://api.service.nhs.uk/ORGANISATION-DATA-TERMINOLOGY-API/fhir/Organization"
        assert is_ods_terminology_request(url) is False

    def test_url_with_additional_path_returns_true(self) -> None:
        """Test that URLs with additional path components still match."""
        url = "https://api.service.nhs.uk/organisation-data-terminology-api/v1/fhir/Organization/123"
        assert is_ods_terminology_request(url) is True


class TestIsMockTestingMode:
    def test_mock_testing_disabled_returns_false(self) -> None:
        """Test that when MOCK_TESTING_SCENARIOS is not 'true', returns False."""
        with patch.dict(os.environ, {"MOCK_TESTING_SCENARIOS": "false"}, clear=False):
            assert is_mock_testing_mode() is False

    def test_mock_testing_not_set_returns_false(self) -> None:
        """Test that when MOCK_TESTING_SCENARIOS is not set, returns False."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_mock_testing_mode() is False

    def test_mock_testing_enabled_dev_environment_returns_true(self) -> None:
        """Test that mock testing enabled in dev environment returns True."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "dev"},
            clear=False,
        ):
            assert is_mock_testing_mode() is True
            assert is_mock_testing_mode() is True

    def test_mock_testing_enabled_test_environment_returns_true(self) -> None:
        """Test that mock testing enabled in test environment returns True."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "test"},
            clear=False,
        ):
            assert is_mock_testing_mode() is True

    def test_mock_testing_enabled_production_environment_raises_error(self) -> None:
        """Test that mock testing in production environment raises ValueError."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "prod"},
            clear=False,
        ):
            with pytest.raises(ValueError) as exc_info:
                is_mock_testing_mode()

            assert (
                "Mock testing scenarios cannot be enabled in environment 'prod'"
                in str(exc_info.value)
            )
            assert "Only allowed in: dev, test" in str(exc_info.value)

    def test_mock_testing_enabled_invalid_environment_raises_error(self) -> None:
        """Test that mock testing in invalid environment raises ValueError."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "staging"},
            clear=False,
        ):
            with pytest.raises(ValueError) as exc_info:
                is_mock_testing_mode()

            assert (
                "Mock testing scenarios cannot be enabled in environment 'staging'"
                in str(exc_info.value)
            )

    def test_mock_testing_case_insensitive_environment(self) -> None:
        """Test that environment check is case insensitive."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "DEV"},
            clear=False,
        ):
            assert is_mock_testing_mode() is True

    def test_mock_testing_case_insensitive_scenarios_flag(self) -> None:
        """Test that MOCK_TESTING_SCENARIOS check is case insensitive."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "TRUE", "ENVIRONMENT": "dev"},
            clear=False,
        ):
            assert is_mock_testing_mode() is True

    def test_mock_testing_no_environment_set_raises_error(self) -> None:
        """Test that mock testing with no environment set raises ValueError."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true"},
            clear=True,
        ):
            with pytest.raises(ValueError) as exc_info:
                is_mock_testing_mode()

            assert "Mock testing scenarios cannot be enabled in environment ''" in str(
                exc_info.value
            )

    @patch("extractor.utils.extractor_utils_logger")
    def test_mock_testing_invalid_environment_logs_error(
        self, mock_logger: MagicMock
    ) -> None:
        """Test that invalid environment logs appropriate error."""
        with patch.dict(
            os.environ,
            {"MOCK_TESTING_SCENARIOS": "true", "ENVIRONMENT": "prod"},
            clear=False,
        ):
            with pytest.raises(ValueError):
                is_mock_testing_mode()

            mock_logger.log.assert_called_once_with(
                OdsETLPipelineLogBase.ETL_UTILS_011, env="prod"
            )
