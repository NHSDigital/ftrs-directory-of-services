import re
from http import HTTPStatus
from urllib.parse import urlparse

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from requests.exceptions import HTTPError

from pipeline.utilities import get_base_apim_api_url, make_request

ods_processor_logger = Logger.get(service="ods_processor")


def fetch_sync_data(date: str) -> list:
    """
    Returns a list of ods organisation records that have been modified since a specified date.
    """
    ods_sync_uri = "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?"
    params = {"LastChangeDate": date}

    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_001,
        params=params,
    )
    response = make_request(ods_sync_uri, params=params)
    organisations = response.json().get("Organisations", [])

    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_002,
        total_orgs=len(organisations),
    )
    return organisations


# To be moved to common package
def validate_ods_code(ods_code: str) -> None:
    if not isinstance(ods_code, str) or not re.match(r"^[A-Za-z0-9]{5,12}$", ods_code):
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_012,
            e=f"Invalid ODS code: {ods_code}",
        )
        err_message = f"Invalid ODS code: '{ods_code}' must match ^[A-Za-z0-9]{{5,12}}$"
        raise ValueError(err_message)


def fetch_ods_organisation_data(ods_code: str) -> dict | None:
    """
    Fetches and validates a FHIR Organization resource for the specified ODS code.
    """
    validate_ods_code(ods_code)
    ods_org_data_uri = (
        "https://directory.spineservices.nhs.uk/STU3/Organization/" + ods_code
    )
    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_003,
        ods_code=ods_code,
    )
    return make_request(ods_org_data_uri, fhir=True)


def fetch_organisation_uuid(ods_code: str) -> str | None:
    """
    Returns DoS UUID based on ODS code.
    """
    validate_ods_code(ods_code)
    base_url = get_base_apim_api_url()
    identifier_param = f"odsOrganisationCode|{ods_code}"
    organisation_get_uuid_uri = (
        base_url + "/Organization?identifier=" + identifier_param
    )

    try:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_028,
            ods_code=ods_code,
        )
        response = make_request(
            organisation_get_uuid_uri,
            method="GET",
            api_key_required=True,
            fhir=True,
        )
        if isinstance(response, dict) and response.get("resourceType") == "Bundle":
            entries = response.get("entry", [])
            for entry in entries:
                resource = entry.get("resource")
                if resource and resource.get("resourceType") == "Organization":
                    return resource.get("id")
            return None
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_030,
            ods_code=ods_code,
            type=response.get("resourceType"),
        )
        raise ValueError(OdsETLPipelineLogBase.ETL_PROCESSOR_007.value.message)

    except HTTPError as http_err:
        if (
            http_err.response is not None
            and http_err.response.status_code == HTTPStatus.NOT_FOUND
        ):
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_007,
            )
            raise ValueError(
                OdsETLPipelineLogBase.ETL_PROCESSOR_007.value.message
            ) from http_err
        raise


def extract_ods_code(link: str) -> str:
    try:
        path = urlparse(link).path
        return path.rstrip("/").split("/")[-1]
    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_012,
            e=e,
        )
        raise
