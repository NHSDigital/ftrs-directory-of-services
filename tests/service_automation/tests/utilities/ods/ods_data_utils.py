"""ODS data utilities for ETL testing."""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import pytest
from playwright.sync_api import APIRequestContext

from utilities.common.constants import ODS_TERMINOLOGY_INT_API_URL
from utilities.infra.api_util import make_api_request_with_retries


class OdsDateSelector:
    """
    Selects a date with at least a minimum number of valid ODS codes.
    Looks back a configurable number of days.
    """

    def __init__(
        self,
        request_context: APIRequestContext,
        lookback_days: int = 7,
        min_codes: int = 10,
    ):
        self.request_context = request_context
        self.lookback_days = lookback_days
        self.min_codes = min_codes

    def find_valid_date(self) -> Tuple[str, List[dict]]:
        today = datetime.now(timezone.utc).date()
        for days_back in range(1, self.lookback_days + 1):
            candidate = today - timedelta(days=days_back)
            date_str = candidate.strftime("%Y-%m-%d")

            org_resources = fetch_ods_organizations(
                self.request_context, date_str, self.min_codes
            )
            if org_resources:
                org_resources = org_resources[: self.min_codes]
                return date_str, org_resources

        pytest.fail(
            f"No date found in last {self.lookback_days} days with at least {self.min_codes} valid ODS codes."
        )


def extract_primary_role_display(org_response: dict) -> Optional[str]:
    extensions = org_response.get("extension", [])
    for ext in extensions:
        if (
            ext.get("url")
            != "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1"
        ):
            continue
        nested_exts = ext.get("extension", [])
        primary_role = any(
            ne.get("url") == "primaryRole" and ne.get("valueBoolean") is True
            for ne in nested_exts
        )
        if primary_role:
            for ne in nested_exts:
                if ne.get("url") == "role":
                    return ne.get("valueCoding", {}).get("display")
    return None


def fetch_ods_organizations(
    request_context: APIRequestContext, last_change_date: str, minimum_count: int
) -> List[dict]:
    terminology_url = f"{ODS_TERMINOLOGY_INT_API_URL}?_lastUpdated={last_change_date}"
    response = make_api_request_with_retries(
        request_context=request_context, method="GET", url=terminology_url
    )

    if response.get("resourceType") != "Bundle":
        return []

    entries = response.get("entry", [])
    if len(entries) < minimum_count:
        return []
    org_resources = []

    for entry in entries:
        resource = entry.get("resource", {})
        if resource.get("resourceType") != "Organization":
            continue

        # Check if organization has a valid ODS code
        for identifier in resource.get("identifier", []):
            if (
                identifier.get("system")
                == "https://fhir.nhs.uk/Id/ods-organization-code"
            ):
                ods_code = identifier.get("value")
                if ods_code:
                    org_resources.append(resource)
                    break

    return org_resources if len(org_resources) >= minimum_count else []


def extract_org_details(org_resources: List[dict]) -> List[Dict[str, Optional[str]]]:
    return [
        {
            "ods_code": next(
                (
                    identifier.get("value")
                    for identifier in org.get("identifier", [])
                    if identifier.get("system")
                    == "https://fhir.nhs.uk/Id/ods-organization-code"
                ),
                None,
            ),
            "type": extract_primary_role_display(org),
            "active": org.get("active"),
            "name": org.get("name"),
            "phone": next(
                (
                    tel.get("value")
                    for tel in org.get("telecom", [])
                    if tel.get("system") == "phone"
                ),
                None,
            ),
        }
        for org in org_resources
        if next(
            (
                identifier.get("value")
                for identifier in org.get("identifier", [])
                if identifier.get("system")
                == "https://fhir.nhs.uk/Id/ods-organization-code"
            ),
            None,
        )
    ]
