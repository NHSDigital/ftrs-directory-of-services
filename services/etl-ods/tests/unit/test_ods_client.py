from http import HTTPStatus
from unittest.mock import MagicMock, patch

from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture

from producer.ods_client import ODSClient


class TestODSClient:
    """Test cases for ODSClient class."""

    def test_init(self) -> None:
        """Test ODSClient initialization."""
        client = ODSClient()
        assert client.logger is not None

    @patch("producer.ods_client.make_common_request")
    @patch("producer.ods_client.build_common_headers")
    @patch.object(ODSClient, "_get_api_key")
    def test_make_request_success(
        self,
        mock_get_api_key: MagicMock,
        mock_build_headers: MagicMock,
        mock_make_request: MagicMock,
    ) -> None:
        """Test successful make_request call."""
        client = ODSClient()
        mock_get_api_key.return_value = "test-api-key"
        mock_build_headers.return_value = {"Accept": "application/fhir+json"}
        mock_make_request.return_value = {
            "resourceType": "Bundle",
            "total": 1,
            "status_code": HTTPStatus.OK,
        }

        result = client.make_request(
            url="https://api.example.com/Organization",
            params={"_count": "10"},
        )

        assert result == {
            "resourceType": "Bundle",
            "total": 1,
            "status_code": HTTPStatus.OK,
        }
        mock_make_request.assert_called_once_with(
            url="https://api.example.com/Organization",
            method="GET",
            params={"_count": "10"},
            headers={"Accept": "application/fhir+json", "apikey": "test-api-key"},
        )

    @patch("producer.ods_client.build_common_headers")
    @patch("producer.ods_client.is_ods_terminology_request")
    def test_build_headers(
        self,
        mock_is_ods_request: MagicMock,
        mock_build_headers: MagicMock,
    ) -> None:
        """Test _build_headers method."""
        client = ODSClient()
        mock_is_ods_request.return_value = True
        mock_build_headers.return_value = {"Accept": "application/fhir+json"}

        with patch.object(client, "_get_api_key", return_value="test-key"):
            result = client._build_headers("https://api.example.com/Organization")

            assert result == {
                "Accept": "application/fhir+json",
                "apikey": "test-key",
            }
            mock_build_headers.assert_called_once()

    @patch("producer.ods_client.is_ods_terminology_request")
    def test_get_api_key_non_ods_url(self, mock_is_ods_request: MagicMock) -> None:
        """Test _get_api_key returns empty string for non-ODS URLs."""
        client = ODSClient()
        mock_is_ods_request.return_value = False

        result = client._get_api_key("https://api.example.com/other")

        assert result == ""
        mock_is_ods_request.assert_called_once_with("https://api.example.com/other")

    @patch("producer.ods_client.SecretManager.get_ods_terminology_api_key")
    @patch("producer.ods_client.is_mock_testing_mode")
    @patch("producer.ods_client.is_ods_terminology_request")
    def test_get_api_key_production_mode(
        self,
        mock_is_ods_request: MagicMock,
        mock_is_mock_mode: MagicMock,
        mock_get_prod_key: MagicMock,
    ) -> None:
        """Test _get_api_key returns production key when not in mock mode."""
        # Setup
        client = ODSClient()
        mock_is_ods_request.return_value = True
        mock_is_mock_mode.return_value = False
        mock_get_prod_key.return_value = "prod-api-key"

        # Execute
        result = client._get_api_key(
            "https://api.service.nhs.uk/organisation-data-terminology-api"
        )

        # Verify
        assert result == "prod-api-key"
        mock_get_prod_key.assert_called_once()

    @patch("producer.ods_client.SecretManager.get_mock_api_key_from_secrets")
    @patch("producer.ods_client.is_mock_testing_mode")
    @patch("producer.ods_client.is_ods_terminology_request")
    def test_get_api_key_mock_mode(
        self,
        mock_is_ods_request: MagicMock,
        mock_is_mock_mode: MagicMock,
        mock_get_mock_key: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """Test _get_api_key returns mock key when in mock mode and logs appropriately."""
        # Setup
        client = ODSClient()
        mock_is_ods_request.return_value = True
        mock_is_mock_mode.return_value = True
        mock_get_mock_key.return_value = "mock-api-key"
        mock_logger = mocker.patch.object(client, "logger")

        # Execute
        result = client._get_api_key(
            "https://api.service.nhs.uk/organisation-data-terminology-api"
        )

        # Verify
        assert result == "mock-api-key"
        mock_get_mock_key.assert_called_once()
        mock_logger.log.assert_called_once_with(OdsETLPipelineLogBase.ETL_UTILS_008)

    def test_add_api_key_to_headers_empty_key(self) -> None:
        """Test _add_api_key_to_headers does nothing when API key is empty."""
        # Setup
        client = ODSClient()
        headers = {"Accept": "application/fhir+json"}

        # Execute
        client._add_api_key_to_headers(headers, "")

        # Verify
        assert headers == {"Accept": "application/fhir+json"}

    @patch("producer.ods_client.is_mock_testing_mode")
    def test_add_api_key_to_headers_production_mode(
        self, mock_is_mock_mode: MagicMock
    ) -> None:
        """Test _add_api_key_to_headers uses 'apikey' header in production."""
        # Setup
        client = ODSClient()
        mock_is_mock_mode.return_value = False
        headers = {"Accept": "application/fhir+json"}

        # Execute
        client._add_api_key_to_headers(headers, "prod-key")

        # Verify
        assert headers == {
            "Accept": "application/fhir+json",
            "apikey": "prod-key",
        }

    @patch("producer.ods_client.is_mock_testing_mode")
    def test_add_api_key_to_headers_mock_mode(
        self, mock_is_mock_mode: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test _add_api_key_to_headers uses 'x-api-key' header in mock mode and logs."""
        # Setup
        client = ODSClient()
        mock_is_mock_mode.return_value = True
        mock_logger = mocker.patch.object(client, "logger")
        headers = {"Accept": "application/fhir+json"}

        # Execute
        client._add_api_key_to_headers(headers, "mock-key")

        # Verify
        assert headers == {
            "Accept": "application/fhir+json",
            "x-api-key": "mock-key",
        }
        mock_logger.log.assert_called_once_with(OdsETLPipelineLogBase.ETL_UTILS_009)

    @patch("producer.ods_client.make_common_request")
    @patch("producer.ods_client.SecretManager.get_ods_terminology_api_key")
    @patch("producer.ods_client.is_mock_testing_mode")
    @patch("producer.ods_client.is_ods_terminology_request")
    def test_make_request_integration(
        self,
        mock_is_ods_request: MagicMock,
        mock_is_mock_mode: MagicMock,
        mock_get_key: MagicMock,
        mock_make_request: MagicMock,
    ) -> None:
        """Test full integration of make_request with all dependencies."""
        # Setup
        client = ODSClient()
        mock_is_ods_request.return_value = True
        mock_is_mock_mode.return_value = False
        mock_get_key.return_value = "integration-key"
        mock_make_request.return_value = {"resourceType": "Bundle", "status_code": 200}

        # Execute
        with patch("producer.ods_client.build_common_headers", return_value={}):
            result = client.make_request(
                url="https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
                params={"_id": "123"},
            )

        # Verify
        assert result == {"resourceType": "Bundle", "status_code": 200}
        mock_make_request.assert_called_once()
        call_kwargs = mock_make_request.call_args.kwargs
        assert (
            call_kwargs["url"]
            == "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
        )
        assert call_kwargs["method"] == "GET"
        assert call_kwargs["params"] == {"_id": "123"}
        assert call_kwargs["headers"]["apikey"] == "integration-key"
