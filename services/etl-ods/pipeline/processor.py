import json
import logging
import re

import requests

from pipeline.load_data import (
    load_data,
)
from pipeline.validators import (
    OrganisationValidator,
    RolesValidator,
    validate_payload,
)

from .extract import (
    extract_display_name,
    extract_ods_code,
    extract_organisation_data,
    fetch_organisation_data,
    fetch_organisation_role,
    fetch_organisation_uuid,
    fetch_sync_data,
)
from .transform import transfrom_into_payload

logger = logging.getLogger()
logger.setLevel(logging.INFO)

STATUS_SUCCESSFUL = 200
BATCH_SIZE = 10


def processor(
    date: str,
) -> None:
    """
    Extract GP practice data from the source, transform to payload and log it out.
    """
    try:
        organisations = fetch_sync_data(date)
        if not organisations:
            logger.info("No organisations found for the given date.")
            return
        total_organisations = len(organisations)
        transformed_batch = []
        for organisation in organisations:
            org_link = organisation.get("OrgLink")
            if not org_link:
                logger.warning("Organisation link is missing in the response.")
                continue
            organisation_ods_code = extract_ods_code(org_link)
            transformed_request = process_organisation(organisation_ods_code)
            transformed_batch.append(transformed_request)

            if (
                len(transformed_batch) == BATCH_SIZE
                or len(transformed_batch) == total_organisations
            ):
                load_data(transformed_batch)
                transformed_batch = []
                total_organisations = total_organisations - BATCH_SIZE

    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching data: {e}")
        raise
    except Exception as e:
        logger.warning(f"Unexpected error: {e}")
        raise


def process_organisation(ods_code: str) -> None:
    """
    Process a single organisation by extracting data, transforming it, and logging the payload.
    """
    try:
        raw_organisation_data = fetch_organisation_data(ods_code)

        relevant_organisation_data = extract_organisation_data(raw_organisation_data)
        validated_organisation_data = validate_payload(
            relevant_organisation_data, OrganisationValidator
        )
        logger.info("Successfully validated organisation data")

        list = validated_organisation_data.Roles.Role
        raw_primary_role_data = fetch_organisation_role(list)
        relevant_role_data = extract_display_name(raw_primary_role_data)
        validated_primary_role_data = validate_payload(
            relevant_role_data, RolesValidator
        )
        logger.info("Successfully validated role data")

        org_uuid = fetch_organisation_uuid(ods_code)

        request_body = transfrom_into_payload(
            validated_organisation_data, validated_primary_role_data
        )
        request = {"path": org_uuid, "body": request_body}
        logger.info(f"Transformed request_body: {json.dumps(request)}")

        return json.dumps(request)

    except Exception as e:
        logger.warning(f"Error processing organisation with ods_code {ods_code}: {e}")


def lambda_handler(event: any, context: any) -> None:
    logging.info("Executing lambda handler")
    try:
        date = event.get("date")
        if not date:
            return {"statusCode": 400, "body": ("Date parameter is required")}
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, date):
            return {"statusCode": 400, "body": "Date must be in YYYY-MM-DD format"}

        processor(date=event["date"])
    except Exception as e:
        logging.info(f"Unexpected error: {e}")
        return {"statusCode": 500, "body": f"Unexpected error: {e}"}
