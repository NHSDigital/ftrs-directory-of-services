import logging
from typing import Annotated

import requests
from typer import Option

STATUS_SUCCESSFUL = 200


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
                ods_code_reponse = requests.get(org_url)
                logging.info(f"Extracted data: {ods_code_reponse.text}")

    except requests.exceptions.RequestException:
        logging.exception("Error fetching data")
