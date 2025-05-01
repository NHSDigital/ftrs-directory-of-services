import logging
import re

import requests

STATUS_SUCCESSFUL = 200


def extract(
    date: str,
) -> None:
    """
    Extract GP practice data from the source and log it out.
    """
    ods_uri = "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?"
    logging.info(f"Extracting data from {ods_uri}")

    params = {"LastChangeDate": date}
    try:
        response = requests.get(ods_uri, params=params)
        if response.status_code == STATUS_SUCCESSFUL:
            response_json = response.json()
            for organisation in response_json["Organisations"]:
                url = organisation.get("OrgLink", "")
                # will need to change if sync endpoint changes schema
                org_url = (
                    "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/"
                    + url.split("organisations/")[1]
                    + "?"
                )
                ods_code_reponse = requests.get(org_url)
                logging.info(f"Extracted data: {ods_code_reponse.text}")
        else:
            logging.exception(f"Unexpected error: {response}")

    except requests.exceptions.RequestException:
        logging.exception("Error fetching data")


def lambda_handler(event: any, context: any) -> None:
    try:
        date = event.get("date")
        if not date:
            return {"statusCode": 400, "body": ("Date parameter is required")}
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, date):
            return {"statusCode": 400, "body": "Date must be in YYYY-MM-DD format"}

        extract(date=event["date"])
    except Exception as e:
        logging.info(f"Unexpected error: {e}")
        return {"statusCode": 500, "body": f"Unexpected error: {e}"}
