from http import HTTPStatus
from urllib.parse import urlparse

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from requests.exceptions import HTTPError

from pipeline.utilities import get_base_crud_api_url, make_request

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


def fetch_ods_organisation_data(ods_code: str) -> dict | None:
    """
    Fetches and validates a FHIR Organization resource for the specified ODS code.
    """
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
    base_url = get_base_crud_api_url()
    organisation_get_uuid_uri = base_url + "/Organization/ods_code/" + ods_code

    try:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_028,
            ods_code=ods_code,
        )
        response = make_request(organisation_get_uuid_uri, sign=True, fhir=True)
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_029_TEMP,
            ods_code=ods_code,
            data=response,
            uuid=organisation_get_uuid_uri,
        )
        return (
            response.get("id", None)
            if isinstance(response, dict)
            else response.json().get("id", None)
        )

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
