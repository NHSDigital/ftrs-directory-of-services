import os
import re
from http import HTTPStatus

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from requests.exceptions import HTTPError

from pipeline.utilities import (
    get_base_apim_api_url,
    get_base_ods_terminology_api_url,
    make_request,
)

DEFAULT_ODS_API_PAGE_LIMIT = 1000

ods_processor_logger = Logger.get(service="ods_processor")


def fetch_outdated_organisations(date: str) -> list[dict]:
    """
    Returns a list of ods organisation FHIR resources that have been modified on a specified date.
    Uses the ODS Terminology API FHIR endpoint with pagination support.
    """
    all_organisations = []
    params = {"_lastUpdated": f"{date}", "_count": _get_page_limit()}
    ods_url = get_base_ods_terminology_api_url()
    page_count = 0
    max_pages = 100  # Safety limit to prevent infinite loops

    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_001,
        date=date,
    )

    while ods_url and page_count < max_pages:
        page_count += 1
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_034,
            date=date,
            page_num=page_count,
        )

        bundle = make_request(ods_url, params=params)
        organisations = _extract_organizations_from_bundle(bundle)

        if organisations:
            all_organisations.extend(organisations)
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_035,
                page_num=page_count,
                page_total=len(organisations),
                cumulative_total=len(all_organisations),
            )

        ods_url = _extract_next_page_url(bundle)
        params = None  # Clear params for subsequent pages

    if not all_organisations:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_020,
            date=date,
        )
        return []

    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_002,
        bundle_total=len(all_organisations),
        total_pages=page_count,
    )
    return all_organisations


def _get_page_limit() -> int:
    raw_value = os.environ.get("ODS_API_PAGE_LIMIT")
    try:
        page_limit = int(raw_value)
        if page_limit > 0:
            return page_limit
    except (ValueError, TypeError):
        pass

    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_021,
        invalid_value=raw_value,
        env_var="ODS_API_PAGE_LIMIT",
        default_value=DEFAULT_ODS_API_PAGE_LIMIT,
    )
    return DEFAULT_ODS_API_PAGE_LIMIT


def _extract_next_page_url(bundle: dict) -> str | None:
    if bundle.get("resourceType") != "Bundle":
        return None

    links = bundle.get("link", [])
    for link in links:
        if link.get("relation") == "next":
            return link.get("url")

    return None


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
            organisation_get_uuid_uri, method="GET", jwt_required=True
        )
        if isinstance(response, dict) and response.get("resourceType") == "Bundle":
            organizations = _extract_organizations_from_bundle(response)
            if organizations:
                return organizations[0].get("id")
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


def validate_ods_code(ods_code: str) -> None:
    if not isinstance(ods_code, str) or not re.match(r"^[A-Za-z0-9]{5,12}$", ods_code):
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_012,
            e=f"Invalid ODS code: {ods_code}",
        )
        err_message = f"Invalid ODS code: '{ods_code}' must match ^[A-Za-z0-9]{{5,12}}$"
        raise ValueError(err_message)


def _extract_organizations_from_bundle(bundle: dict) -> list[dict]:
    organizations = []
    if bundle.get("resourceType") == "Bundle":
        entries = bundle.get("entry", [])
        for entry in entries:
            resource = entry.get("resource")
            if resource and resource.get("resourceType") == "Organization":
                organizations.append(resource)
    return organizations
