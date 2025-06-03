import logging
from http import HTTPStatus
from urllib.parse import urlparse

from requests.exceptions import HTTPError

from pipeline.utilities import get_base_crud_api_url, make_request

logger = logging.getLogger()
logger.setLevel(logging.INFO)

STATUS_SUCCESSFUL = 200


def fetch_sync_data(date: str) -> dict:
    """
    Returns a list of ods organisation records that have been modified since a specified date.
    """
    ods_sync_uri = "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?"
    params = {"LastChangeDate": date}

    logging.info(f"Fetching data from sync endpoint with params: {params}")
    response = make_request(ods_sync_uri, params=params)
    organisations = response.json().get("Organisations", [])

    logging.info(
        f"Fetching data from sync endpoint returned {len(organisations)} outdated organisations"
    )
    return organisations


def fetch_organisation_data(ods_code: str) -> str:
    """
    Returns a dataset of a single organisation for the specified ODS code.
    """
    ods_org_data_uri = (
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/" + ods_code
    )
    logging.info(f"Fetching organisation data for code: {ods_code}")
    response = make_request(ods_org_data_uri)
    organisation = response.json().get("Organisation", [])
    if not organisation:
        logger.warning(
            f"No organisation found in the response for the given ODS code {ods_code}"
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
        err_msg = "No primary role found in the roles list."
        logger.warning(err_msg)
        raise ValueError(err_msg)
    ods_role_data_uri = (
        f"https://directory.spineservices.nhs.uk/ORD/2-0-0/roles/{primary_role_id}"
    )
    logger.info(f"Fetching role data for ID: {primary_role_id}")
    response = make_request(ods_role_data_uri)
    return response.json()


def fetch_organisation_uuid(ods_code: str) -> str:
    """
    Returns DoS UUID based on ODS code
    """
    base_url = get_base_crud_api_url()
    organisation_get_uuid_uri = base_url + "/organisation/ods_code/" + ods_code

    try:
        response = make_request(organisation_get_uuid_uri, sign=True)
        return response.json().get("id", None)

    except HTTPError as http_err:
        if http_err.response.status_code == HTTPStatus.NOT_FOUND:
            err_msg = "Organisation not found in database"
            logger.warning(err_msg)
            raise ValueError(err_msg) from http_err
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
            logger.warning(f"Missing key in organisation payload: {key}")
    return result


def extract_display_name(payload: dict) -> str | None:
    roles = payload.get("Roles")

    if not isinstance(roles, list):
        err_msg = "Roles payload extraction failed: role is not a list"
        logger.warning(err_msg)
        raise TypeError(err_msg)

    for role in roles:
        if not isinstance(role, dict):
            logger.warning(f"Invalid role format: {role}")
            continue
        if role.get("primaryRole") == "true":
            return {"displayName": role.get("displayName")}


def extract_contact(payload: dict) -> dict | None:
    contacts = payload.get("Contacts", {}).get("Contact", [])
    if not contacts:
        return None
    for contact in contacts:
        if not isinstance(contact, dict):
            logger.warning(f"Invalid contact format: {contact}")
        if contact.get("type") == "tel":
            return {"type": "tel", "value": contact.get("value")}


def extract_ods_code(link: str) -> str:
    try:
        path = urlparse(link).path
        return path.rstrip("/").split("/")[-1]
    except Exception as e:
        logger.warning(f"ODS code extraction failed: {e}")
        raise
