from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.http_client import build_headers as build_common_headers
from common.http_client import make_request as make_common_request

from .secrets import SecretManager
from .utils import is_mock_testing_mode, is_ods_terminology_request

ods_client_logger = Logger.get(service="ods_client")


class ODSClient:
    def __init__(self) -> None:
        self.logger = ods_client_logger

    def make_request(
        self,
        url: str,
        params: dict | None = None,
        **kwargs: dict,
    ) -> dict:
        """
        Make a request to ODS Terminology API with proper authentication and headers.
        """
        headers = self._build_headers(url=url)

        return make_common_request(
            url=url,
            method="GET",
            params=params,
            headers=headers,
            **kwargs,
        )

    def _build_headers(
        self,
        url: str,
    ) -> dict:
        """Build headers for ODS API requests."""
        headers = build_common_headers()

        # Add ODS-specific API key
        api_key = self._get_api_key(url)
        self._add_api_key_to_headers(headers, api_key)

        return headers

    def _get_api_key(self, url: str) -> str:
        """Get the appropriate API key for the URL."""
        if not is_ods_terminology_request(url):
            return ""

        if is_mock_testing_mode():
            self.logger.log(OdsETLPipelineLogBase.ETL_UTILS_008)
            return SecretManager.get_mock_api_key_from_secrets()

        return SecretManager.get_ods_terminology_api_key()

    def _add_api_key_to_headers(self, headers: dict, api_key: str) -> None:
        """Add API key to headers with the appropriate header name."""
        if not api_key:
            return

        if is_mock_testing_mode():
            self.logger.log(OdsETLPipelineLogBase.ETL_UTILS_009)
            headers["x-api-key"] = api_key
        else:
            headers["apikey"] = api_key
