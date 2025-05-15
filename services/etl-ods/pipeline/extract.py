import logging
import os
from urllib.parse import urlparse

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

STATUS_SUCCESSFUL = 200
NOT_FOUND = 404


def make_request(url: str, params: dict = None, timeout: int = 20) -> dict:
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == NOT_FOUND and url.startswith(
            os.environ["ORGANISATION_API_URL"]
        ):
            raise ValueError("Test")
        logger.info(
            f"HTTP error occurred: {http_err} - Status Code: {response.status_code}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.info(f"Request to {url} failed: {e}")
        raise


def fetch_sync_data(date: str) -> dict:
    """
    Returns a list of ods organisation records that have been modified since a specified date.
    """
    ods_sync_uri = "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?"
    params = {"LastChangeDate": date}

    logging.info(f"Fetching data from sync endpoint with params: {params}")
    response = make_request(ods_sync_uri, params=params)
    organisations = response.get("Organisations", [])

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
    organisation = response.get("Organisation", [])
    if not organisation:
        logger.warning("No organisations found in the response.")

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
        logger.warning("No primary role found in the roles list.")
        raise ValueError("Test2")
    ods_role_data_uri = (
        f"https://directory.spineservices.nhs.uk/ORD/2-0-0/roles/{primary_role_id}"
    )
    logger.info(f"Fetching role data for ID: {primary_role_id}")
    return make_request(ods_role_data_uri)


def fetch_organisation_uuid(ods_code: str) -> str:
    """
    Returns DoS UUID based on ODS code
    """
    organisation_get_uuid_uri = (
        os.environ["ORGANISATION_API_URL"] + "/ods_code/" + ods_code
    )
    return make_request(organisation_get_uuid_uri).get("id", None)


def extract_organisation_data(payload: dict) -> dict:
    try:
        return {
            "Name": payload.get("Name"),
            "Status": payload.get("Status"),
            "Roles": payload.get("Roles"),
            "Contacts": extract_telecom(payload),
        }
    except AttributeError as e:
        logger.info(f"Organisation payload extraction failed: {e}")
        raise


def extract_display_name(payload: dict) -> str | None:
    roles = payload.get("Roles")
    try:
        for role in roles:
            if role.get("primaryRole") == "true":
                return {"displayName": role.get("displayName")}
    except AttributeError as e:
        logger.info(f"Roles payload extraction failed: {e}")
        raise


def extract_contact(payload: dict) -> dict | None:
    contacts = payload.get("Contacts", {}).get("Contact", [])
    try:
        if not contacts:
            return None
        for contact in contacts:
            if contact.get("type") == "tel":
                return {"type": "tel", "value": contact.get("value")}
    except AttributeError as e:
        logger.info(f"Contact payload extraction failed: {e}")
        raise


def extract_telecom(payload: dict) -> str | None:
    try:
        contacts = payload.Contacts
        if not contacts:
            return None
        for contact in contacts:
            if isinstance(contact, tuple):
                contact_type, contact_items = contact
                if contact_type == "Contact" and isinstance(contact_items, list):
                    for contact_item in contact_items:
                        if contact_item.type == "tel":
                            return contact_item.value  # tidy up this
    except AttributeError as e:
        logger.info(f"Telecom payload extraction failed: {e}")
        raise


def extract_ods_code(link: str) -> str:
    try:
        path = urlparse(link).path
        return path.rstrip("/").split("/")[-1]
    except AttributeError as e:
        logger.info(f"ODS code extraction failed: {e}")
        raise
