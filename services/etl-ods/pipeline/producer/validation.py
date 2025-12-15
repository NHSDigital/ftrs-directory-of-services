"""Business logic for classifying ODS organizations."""

from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
from ftrs_common.logger import Logger
from ftrs_data_layer.domain.enums import OrganisationType
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

# Role codes
PRESCRIBING_COST_CENTRE_CODE = "RO177"
GP_PRACTICE_ROLE_CODE = "RO76"

ods_validation_logger = Logger.get(service="ods_validation")


def get_permitted_org_type(ods_org: dict) -> str | None:
    """
    Determine permitted organization type from ODS organization.

    Args:
        ods_org: ODS FHIR organization dictionary

    Returns:
        Organization type if permitted, None otherwise
    """
    _mapper = OrganizationMapper()
    ods_validation_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_033,
    )
    if is_gp(ods_org, _mapper):
        return OrganisationType.GP_PRACTICE
    return None


def is_gp(ods_org: dict, _mapper: OrganizationMapper) -> bool:
    """
    Check if ODS organization qualifies as a GP Practice.

    Business Rules:
    1. Must have RO177 (Prescribing Cost Centre) role AND
    2. Must have at least one GP Practice role code (RO76, RO80, or RO87)
    3. Both conditions must be met to qualify as GP Practice

    Args:
        ods_org: ODS FHIR organization dictionary
        _mapper: OrganizationMapper instance for extracting role codes

    Returns:
        True if organization qualifies as GP Practice, False otherwise
    """
    ods_code = _mapper._extract_ods_code_from_identifiers(ods_org.get("identifier", []))
    role_codes = _mapper.get_all_role_codes(ods_org)

    if PRESCRIBING_COST_CENTRE_CODE not in role_codes:
        reason = f"Role {PRESCRIBING_COST_CENTRE_CODE} not found"
        ods_validation_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_032,
            ods_code=ods_code,
            reason=reason,
        )
        return False

    has_gp_roles = GP_PRACTICE_ROLE_CODE in role_codes

    if not has_gp_roles:
        ods_validation_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_032,
            ods_code=ods_code,
            reason="No GP Practice mapped roles found.",
        )
        return False

    ods_validation_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_031,
        ods_code=ods_code,
        org_type=OrganisationType.GP_PRACTICE,
        reason="Type maps to GP Practice.",
    )
    return True
