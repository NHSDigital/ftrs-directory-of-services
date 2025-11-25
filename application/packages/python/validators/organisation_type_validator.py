from ftrs_data_layer.domain.enums import OrganisationType


class OrganisationTypeValidator:
    """Validates organization type and non-primary role combinations."""

    # Role codes from ODS
    PRESCRIBING_COST_CENTRE_CODE = "RO177"
    GP_PRACTICE_ROLE_CODE = "RO76"
    OUT_OF_HOURS_ROLE_CODE = "RO80"
    WALK_IN_CENTRE_ROLE_CODE = "RO87"
    PHARMACY_ROLE_CODE = "RO182"

    # Valid primary types (only these can be primary)
    VALID_PRIMARY_TYPES = {
        OrganisationType.PRESCRIBING_COST_CENTRE,
        OrganisationType.PHARMACY,
    }

    # Types that Prescribing Cost Centre can map to as non-primary roles
    PRESCRIBING_COST_CENTRE_ALLOWED_NON_PRIMARY = {
        OrganisationType.GP_PRACTICE,
        OrganisationType.OUT_OF_HOURS_COST_CENTRE,
        OrganisationType.WALK_IN_CENTRE,
    }

    @classmethod
    def validate_type_combination(
        cls,
        primary_type: OrganisationType,
        non_primary_roles: list[OrganisationType],
    ) -> tuple[bool, str | None]:
        """
        Validate that a primary type and non-primary roles combination is permitted.

        Valid combinations:
        1. Prescribing Cost Centre (primary):
            - Must have at least one of: GP Practice, Out of Hours Cost Centre, Walk-In Centre
            - Can have multiple of these as non-primary roles
        2. Pharmacy (primary):
            - Must be standalone (no non-primary roles allowed)

        Args:
            primary_type: The primary organization type
            non_primary_roles: List of non-primary organization roles

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
        """
        error_message = None

        # Validate primary type is allowed
        if primary_type not in cls.VALID_PRIMARY_TYPES:
            error_message = (
                f"Invalid primary organization type: '{primary_type.value}'. "
                "Only 'Prescribing Cost Centre' and 'Pharmacy' are permitted as primary types."
            )

        # Handle Pharmacy - must be standalone
        elif primary_type == OrganisationType.PHARMACY and non_primary_roles:
            error_message = (
                f"{primary_type.value} cannot have non-primary roles. "
                f"Found: {[role.value for role in non_primary_roles]}"
            )

        # Handle Prescribing Cost Centre
        elif primary_type == OrganisationType.PRESCRIBING_COST_CENTRE:
            # Must have at least one non-primary role
            if not non_primary_roles:
                error_message = (
                    f"{primary_type.value} must have at least one non-primary role"
                )

            # Check for duplicate roles
            elif len(non_primary_roles) != len(set(non_primary_roles)):
                error_message = "Duplicate non-primary roles are not allowed."

            # Validate each non-primary role is allowed
            else:
                invalid_roles = [
                    role
                    for role in non_primary_roles
                    if role not in cls.PRESCRIBING_COST_CENTRE_ALLOWED_NON_PRIMARY
                ]
                if invalid_roles:
                    error_message = (
                        f"Non-primary role '{invalid_roles[0].value}' is not permitted for "
                        f"primary type '{primary_type.value}'."
                    )

        return (error_message is None, error_message)
