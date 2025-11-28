from ftrs_data_layer.domain.enums import OrganisationTypeCode

# Valid primary types (only these can be primary)
VALID_PRIMARY_TYPE_CODES = {
    OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
    OrganisationTypeCode.PHARMACY_ROLE_CODE,
}

# Types that Prescribing Cost Centre can map to as non-primary roles
PRESCRIBING_COST_CENTRE_ALLOWED_NON_PRIMARY_TYPE_CODES = {
    OrganisationTypeCode.GP_PRACTICE_ROLE_CODE,
    OrganisationTypeCode.OUT_OF_HOURS_ROLE_CODE,
    OrganisationTypeCode.WALK_IN_CENTRE_ROLE_CODE,
}


class OrganisationTypeValidator:
    @classmethod
    def validate_type_combination(
        cls,
        primary_type_code: OrganisationTypeCode,
        non_primary_role_codes: list[OrganisationTypeCode],
    ) -> tuple[bool, str | None]:
        """
        Validate that a primary type and non-primary roles combination is permitted.

        Args:
            primary_type_code: The primary organization role code
            non_primary_role_codes: List of non-primary organization role codes

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
        """
        error_message = None

        # Handle Pharmacy - must be standalone
        if (
            primary_type_code == OrganisationTypeCode.PHARMACY_ROLE_CODE
            and non_primary_role_codes
        ):
            error_message = (
                f"{primary_type_code.value} cannot have non-primary roles. "
                f"Found: {[role.value for role in non_primary_role_codes]}"
            )

        # Handle Prescribing Cost Centre
        elif primary_type_code == OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE:
            # Must have at least one non-primary role
            if not non_primary_role_codes:
                error_message = (
                    f"{primary_type_code.value} must have at least one non-primary role"
                )

            # Check for duplicate roles
            elif len(non_primary_role_codes) != len(set(non_primary_role_codes)):
                error_message = "Duplicate non-primary roles are not allowed."

            # Validate each non-primary role is allowed
            else:
                invalid_roles = [
                    role
                    for role in non_primary_role_codes
                    if role
                    not in PRESCRIBING_COST_CENTRE_ALLOWED_NON_PRIMARY_TYPE_CODES
                ]
                if invalid_roles:
                    error_message = (
                        f"Non-primary role '{invalid_roles[0].value}' is not permitted for "
                        f"primary type '{primary_type_code.value}'."
                    )

        return (error_message is None, error_message)
