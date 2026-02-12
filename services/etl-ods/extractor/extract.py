import os

from ftrs_common.logger import Logger
from ftrs_data_layer.domain.enums import OrganisationTypeCode
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.url_config import get_base_ods_terminology_api_url
from extractor.ods_client import ODSClient

DEFAULT_ODS_API_PAGE_LIMIT = 1000
RESOURCE_TYPE_BUNDLE = "Bundle"
RESOURCE_TYPE_ORGANIZATION = "Organization"
LINK_RELATION_NEXT = "next"

ods_extractor_logger = Logger.get(service="ods_extractor")
ods_client = ODSClient()


def fetch_outdated_organisations(date: str) -> list[dict]:
    """
    Returns a list of ods organisation FHIR resources that have been modified on a specified date.
    Uses the ODS Terminology API FHIR endpoint with pagination support.
    """
    all_organisations = []
    params = _build_ods_query_params(date)
    ods_url = get_base_ods_terminology_api_url()
    page_count = 0
    max_pages = 100  # Safety limit to prevent infinite loops

    ods_extractor_logger.log(
        OdsETLPipelineLogBase.ETL_EXTRACTOR_001,
        date=date,
    )

    while ods_url and page_count < max_pages:
        page_count += 1
        ods_extractor_logger.log(
            OdsETLPipelineLogBase.ETL_EXTRACTOR_034,
            date=date,
            page_num=page_count,
        )

        bundle = ods_client.make_request(ods_url, params=params)
        organisations = _extract_organizations_from_bundle(bundle)

        if organisations:
            all_organisations.extend(organisations)
            ods_extractor_logger.log(
                OdsETLPipelineLogBase.ETL_EXTRACTOR_035,
                page_num=page_count,
                page_total=len(organisations),
                cumulative_total=len(all_organisations),
            )

        ods_url = _extract_next_page_url(bundle)
        params = None  # Clear params for subsequent pages

    if not all_organisations:
        ods_extractor_logger.log(
            OdsETLPipelineLogBase.ETL_EXTRACTOR_020,
            date=date,
        )
        return []

    ods_extractor_logger.log(
        OdsETLPipelineLogBase.ETL_EXTRACTOR_002,
        bundle_total=len(all_organisations),
        total_pages=page_count,
    )
    return all_organisations


def _build_ods_query_params(date: str) -> list[tuple[str, str]]:
    return [
        ("_lastUpdated", f"{date}"),
        ("_count", str(_get_page_limit())),
        ("roleCode", OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE.value),
        ("roleCode", OrganisationTypeCode.GP_PRACTICE_ROLE_CODE.value),
    ]


def _get_page_limit() -> int:
    raw_value = os.environ.get("ODS_API_PAGE_LIMIT")
    try:
        page_limit = int(raw_value)
        if page_limit > 0:
            return page_limit
    except (ValueError, TypeError):
        pass

    ods_extractor_logger.log(
        OdsETLPipelineLogBase.ETL_EXTRACTOR_021,
        invalid_value=raw_value,
        env_var="ODS_API_PAGE_LIMIT",
        default_value=DEFAULT_ODS_API_PAGE_LIMIT,
    )
    return DEFAULT_ODS_API_PAGE_LIMIT


def _extract_next_page_url(bundle: dict) -> str | None:
    if bundle.get("resourceType") != RESOURCE_TYPE_BUNDLE:
        return None

    links = bundle.get("link", [])
    for link in links:
        if link.get("relation") == LINK_RELATION_NEXT:
            return link.get("url")

    return None
    if not isinstance(ods_code, str) or not re.match(ODS_CODE_PATTERN, ods_code):
        ods_extractor_logger.log(
            OdsETLPipelineLogBase.ETL_EXTRACTOR_012,
            e=f"Invalid ODS code: {ods_code}",
        )
        err_message = f"Invalid ODS code: '{ods_code}' must match {ODS_CODE_PATTERN}"
        raise ValueError(err_message)


def _extract_organizations_from_bundle(bundle: dict) -> list[dict]:
    organizations = []
    if bundle.get("resourceType") == RESOURCE_TYPE_BUNDLE:
        entries = bundle.get("entry", [])
        for entry in entries:
            resource = entry.get("resource")
            if resource and resource.get("resourceType") == "Organization":
                organizations.append(resource)
    return organizations
