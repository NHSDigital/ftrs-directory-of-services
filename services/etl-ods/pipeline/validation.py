"""Business logic for classifying ODS organizations."""

from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
from ftrs_common.logger import Logger
from ftrs_data_layer.domain.enums import OrganisationType
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

# Role codes
PRESCRIBING_COST_CENTRE_CODE = "RO177"
GP_PRACTICE_ROLE_CODE = "RO76"
OUT_OF_HOURS_ROLE_CODE = "RO80"
WALK_IN_CENTRE_ROLE_CODE = "RO87"
PHARMACY_ROLE_CODE = "RO182"


ROLE_TO_ORG_TYPE = {
    GP_PRACTICE_ROLE_CODE: OrganisationType.GP_PRACTICE,
    OUT_OF_HOURS_ROLE_CODE: OrganisationType.OUT_OF_HOURS_COST_CENTRE,
    WALK_IN_CENTRE_ROLE_CODE: OrganisationType.WALK_IN_CENTRE,
}

PERMITTED_ROLE_COMBINATIONS = {
    PRESCRIBING_COST_CENTRE_CODE: [
        GP_PRACTICE_ROLE_CODE,
        OUT_OF_HOURS_ROLE_CODE,
        WALK_IN_CENTRE_ROLE_CODE,
    ],
    PHARMACY_ROLE_CODE: [],
}

ods_validation_logger = Logger.get(service="ods_validation")


def get_permitted_org_type(ods_org: dict) -> tuple[str | None, list[str]]:
    """
    Determine permitted organization type and non-primary roles from ODS organization.

    Args:
        ods_org: ODS FHIR organization dictionary

    Returns:
        Tuple of (primary organization type, list of non-primary role types)
        Returns (None, []) if organization is not permitted
    """
    _mapper = OrganizationMapper()
    ods_code = _mapper._extract_ods_code_from_identifiers(ods_org.get("identifier", []))

    ods_validation_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_033,
    )

    role_codes = _mapper.get_all_role_codes(ods_org)

    # Check if Prescribing Cost Centre is present
    if PRESCRIBING_COST_CENTRE_CODE in role_codes:
        primary_type, non_primary_types = _validate_prescribing_cost_centre_roles(
            role_codes, ods_code
        )
        return primary_type, non_primary_types

    if PHARMACY_ROLE_CODE in role_codes and len(role_codes) > 1:
        ods_validation_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_032,
            ods_code=ods_code,
            reason="Pharmacy cant map with other roles.",
        )
        return None, []

    if PHARMACY_ROLE_CODE in role_codes:
        primary_type = OrganisationType.PHARMACY.value
        ods_validation_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_031,
            ods_code=ods_code,
            org_type=primary_type,
            reason="Pharmacy organization mapped with no non-primary roles.",
        )
        return primary_type, []

    ods_validation_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_032,
        ods_code=ods_code,
        reason="No permitted primary role found.",
    )
    return None, []


def _validate_prescribing_cost_centre_roles(
    role_codes: list[str], ods_code: str
) -> tuple[str | None, list[str]]:
    """
    Validate roles for Prescribing Cost Centre organizations.

    Args:
        role_codes: List of all role codes from ODS
        ods_code: Organization ODS code for logging

    Returns:
        Tuple of (primary type, list of non-primary types)
    """
    allowed_non_primary = PERMITTED_ROLE_COMBINATIONS[PRESCRIBING_COST_CENTRE_CODE]

    # Find matching non-primary roles
    matched_roles = [code for code in role_codes if code in allowed_non_primary]

    if not matched_roles:
        ods_validation_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_032,
            ods_code=ods_code,
            reason="No permitted non-primary roles found for Prescribing Cost Centre.",
        )
        return None, []

    # Determine primary type (use first matched role)
    primary_type = ROLE_TO_ORG_TYPE.get(matched_roles[0])

    # Map remaining roles to non-primary types
    non_primary_types = [
        ROLE_TO_ORG_TYPE[code] for code in matched_roles[1:] if code in ROLE_TO_ORG_TYPE
    ]

    ods_validation_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_031,
        ods_code=ods_code,
        org_type=primary_type,
        reason=f"Role mapping is valid with Non-primary types: {non_primary_types}",
    )

    return primary_type, non_primary_types
