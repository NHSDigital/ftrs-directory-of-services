import re
from http import HTTPStatus

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from requests.exceptions import HTTPError

from common.apim_client import make_apim_request
from common.error_handling import handle_http_error
from common.exceptions import PermanentProcessingError
from common.url_config import get_base_apim_api_url

ODS_CODE_PATTERN = r"^[A-Za-z0-9]{1,12}$"
RESOURCE_TYPE_BUNDLE = "Bundle"

transformer_uuid_logger = Logger.get(service="ods_transformer")


def fetch_organisation_uuid(ods_code: str, message_id: str) -> str | None:
    validate_ods_code(ods_code, message_id)
    base_url = get_base_apim_api_url()
    identifier_param = f"odsOrganisationCode|{ods_code}"
    organisation_get_uuid_uri = (
        base_url + "/Organization?identifier=" + identifier_param
    )

    try:
        transformer_uuid_logger.log(
            OdsETLPipelineLogBase.ETL_TRANSFORMER_031,
            ods_code=ods_code,
        )
        response = make_apim_request(organisation_get_uuid_uri, method="GET")
        if (
            isinstance(response, dict)
            and response.get("resourceType") == RESOURCE_TYPE_BUNDLE
        ):
            organizations = _extract_organizations_from_bundle(response)
            if organizations:
                uuid = organizations[0].get("id")
                return uuid
            return None

        transformer_uuid_logger.log(
            OdsETLPipelineLogBase.ETL_TRANSFORMER_032,
            ods_code=ods_code,
            type=response.get("resourceType"),
        )
        err_msg = f"Unexpected response type: {response.get('resourceType')}"
        raise PermanentProcessingError(
            message_id=message_id,
            status_code=400,
            response_text=err_msg,
        )

    except HTTPError as http_err:
        # Special handling for 404 - log specific message before delegating to error handler
        if (
            http_err.response is not None
            and http_err.response.status_code == HTTPStatus.NOT_FOUND
        ):
            transformer_uuid_logger.log(
                OdsETLPipelineLogBase.ETL_TRANSFORMER_033,
                ods_code=ods_code,
            )

        # Delegate to centralized error handler for consistent classification
        # - Retryable: 408, 429, 500, 502, 503, 504
        # - Permanent: 400, 401, 403, 404, 405, 406, 409, 410, 412, 422
        handle_http_error(http_err, message_id, ods_code)


def validate_ods_code(ods_code: str, message_id: str) -> None:
    """Validate ODS code format."""
    if not isinstance(ods_code, str) or not re.match(ODS_CODE_PATTERN, ods_code):
        err_message = f"Invalid ODS code: '{ods_code}' must match {ODS_CODE_PATTERN}"
        transformer_uuid_logger.log(
            OdsETLPipelineLogBase.ETL_TRANSFORMER_034,
            ods_code=ods_code,
            e=err_message,
        )
        raise PermanentProcessingError(
            message_id=message_id,
            status_code=400,
            response_text=err_message,
        )


def _extract_organizations_from_bundle(bundle: dict) -> list[dict]:
    """Extract Organization resources from a FHIR Bundle."""
    organizations = []
    if bundle.get("resourceType") == RESOURCE_TYPE_BUNDLE:
        entries = bundle.get("entry", [])
        for entry in entries:
            resource = entry.get("resource")
            if resource and resource.get("resourceType") == "Organization":
                organizations.append(resource)
    return organizations
