import logging
import time
from typing import Annotated

import requests
from typer import Option

STATUS_SUCCESSFUL = 200
STATUS_RATE_LIMITED = 429


def make_request_with_retry(url: str, max_retries: int = 3) -> requests.Response:
    """
    Make a request with exponential backoff retry logic for rate limits.
    """
    retries = 0
    backoff_time = 1

    while retries <= max_retries:
        try:
            response = requests.get(url)

            if response.status_code == STATUS_RATE_LIMITED:
                if retries == max_retries:
                    response.raise_for_status()

                wait_time = backoff_time
                logging.warning(
                    f"Rate limit hit ({response.status_code}). Retrying in {wait_time} seconds."
                )
                time.sleep(wait_time)
                backoff_time *= 2
                retries += 1
            else:
                return response

        except requests.exceptions.RequestException:
            logging.exception("Error fetching data")
            return None

    return None


def extract(
    date: Annotated[str, Option(..., help="last changed date format YYYY-MM-DD")],
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
                ods_code_reponse = make_request_with_retry(org_url)
                logging.info(f"Extracted data: {ods_code_reponse.text}")

    except requests.exceptions.RequestException:
        logging.exception("Error fetching data")
