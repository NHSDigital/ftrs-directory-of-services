from http import HTTPStatus
from urllib.parse import urlparse

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from requests.exceptions import HTTPError

from pipeline.utilities import get_base_crud_api_url, make_request

STATUS_SUCCESSFUL = 200

ods_processor_logger = Logger.get(service="ods_processor")


def fetch_sync_data(date: str) -> dict:
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


def fetch_organisation_data(ods_code: str) -> str:
    """
    Returns a dataset of a single organisation for the specified ODS code.
    """
    ods_org_data_uri = (
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/" + ods_code
    )
    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_003,
        ods_code=ods_code,
    )
    response = make_request(ods_org_data_uri)
    organisation = response.json().get("Organisation", [])
    if not organisation:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_004,
            ods_code=ods_code,
        )

    return organisation


def fetch_organisation_role(roles: list) -> str:
    """
    Returns CodeSystems information i.e. display name for Roles when searched for a specified role id
    """
    for role in roles:
        if role.primaryRole is True:
            primary_role_id = role.id
            break
        else:
            primary_role_id = None

    if not primary_role_id:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_005,
        )
        raise ValueError(OdsETLPipelineLogBase.ETL_PROCESSOR_005.value)
    ods_role_data_uri = (
        f"https://directory.spineservices.nhs.uk/ORD/2-0-0/roles/{primary_role_id}"
    )
    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_006,
        primary_role_id=primary_role_id,
    )
    response = make_request(ods_role_data_uri)
    return response.json()


def fetch_organisation_uuid(ods_code: str) -> str:
    """
    Returns DoS UUID based on ODS code
    """
    base_url = get_base_crud_api_url()
    organisation_get_uuid_uri = base_url + "/organisation/ods_code/" + ods_code

    try:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_028,
            ods_code=ods_code,
        )
        response = make_request(organisation_get_uuid_uri, sign=True)
        return response.json().get("id", None)

    except HTTPError as http_err:
        if http_err.response.status_code == HTTPStatus.NOT_FOUND:
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_007,
            )
            raise ValueError(
                OdsETLPipelineLogBase.ETL_PROCESSOR_007.value.message
            ) from http_err

        raise


def extract_organisation_data(payload: dict) -> dict:
    result = {
        "Name": payload.get("Name"),
        "Status": payload.get("Status"),
        "Roles": payload.get("Roles"),
        "Contact": extract_contact(payload),
    }
    for key, value in result.items():
        if value is None and key != "Contact":
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_008,
                key=key,
            )
    return result


def extract_display_name(payload: dict) -> str | None:
    roles = payload.get("Roles")

    if not isinstance(roles, list):
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_009,
        )
        raise TypeError(OdsETLPipelineLogBase.ETL_PROCESSOR_009.value)

    for role in roles:
        if not isinstance(role, dict):
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_010,
                role=role,
            )
            continue
        if role.get("primaryRole") == "true":
            return {"displayName": role.get("displayName")}


def extract_contact(payload: dict) -> dict | None:
    contacts = payload.get("Contacts", {}).get("Contact", [])
    if not contacts:
        return None
    for contact in contacts:
        if not isinstance(contact, dict):
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_011,
                contact=contact,
            )
        if contact.get("type") == "tel":
            return {"type": "tel", "value": contact.get("value")}


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
