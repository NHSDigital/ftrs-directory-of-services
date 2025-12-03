from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException
from fhir.resources.R4B.organization import Organization as FhirOrganisation
from ftrs_common.fhir.fhir_validator import FhirValidator
from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
from ftrs_common.logger import Logger
from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.domain.enums import OrganisationTypeCode
from ftrs_data_layer.domain.organisation import LegalDates
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

from organisations.app.models.organisation import LegalDateField
from organisations.app.services.validators import validate_type_combination


class OrganisationService:
    def __init__(
        self,
        org_repository: AttributeLevelRepository[Organisation],
        logger: Logger | None = None,
        mapper: OrganizationMapper | None = None,
    ) -> None:
        self.org_repository = org_repository
        self.logger = logger or Logger.get(service="crud_organisation_logger")
        self.organisation_mapper = mapper or OrganizationMapper()

    def process_organisation_update(
        self,
        organisation_id: str,
        fhir_org: dict,
    ) -> bool:
        """
        Update an organisation from a FHIR Organisation resource.
        """
        fhir_organisation = FhirValidator.validate(fhir_org, FhirOrganisation)
        ods_code = None

        if (
            hasattr(fhir_org, "identifier")
            and fhir_org.identifier
            and hasattr(fhir_org.identifier[0], "value")
        ):
            ods_code = fhir_org.identifier[0].value
        stored_organisation = self._get_stored_organisation(organisation_id, ods_code)
        organisation = self.organisation_mapper.from_fhir(fhir_organisation)
        outdated_fields = self._get_outdated_fields(stored_organisation, organisation)

        if not outdated_fields:
            self.logger.log(
                CrudApisLogBase.ORGANISATION_007,
                organisation_id=organisation_id,
            )
            return False

        self._apply_updates(stored_organisation, outdated_fields)
        self.org_repository.update(organisation_id, stored_organisation)
        self.logger.log(
            CrudApisLogBase.ORGANISATION_008,
            organisation_id=organisation_id,
        )
        return True

    def create_organisation(self, organisation: Organisation) -> Organisation:
        # if the organisation already exists, we log it and raise an error
        existing_organisation = self.org_repository.get_by_ods_code(
            organisation.identifier_ODS_ODSCode
        )
        if existing_organisation:
            self.logger.log(
                CrudApisLogBase.ORGANISATION_013,
                ods_code=organisation.identifier_ODS_ODSCode,
            )
            raise HTTPException(
                status_code=409, detail="Organisation with this ODS code already exists"
            )
        # If the organisation already has an ID, we log it and generate a new one
        if organisation.id is not None:
            self.logger.log(
                CrudApisLogBase.ORGANISATION_014,
                organisation_id=organisation.id,
            )
            organisation.id = uuid4()
        self.org_repository.create(organisation)
        return organisation

    def _apply_updates(
        self, existing_organisation: Organisation, outdated_fields: dict
    ) -> Organisation:
        """
        Apply outdated fields to the existing organisation.
        """
        self.logger.log(
            CrudApisLogBase.ORGANISATION_009,
            organisation_id=existing_organisation.id,
        )
        for field, value in outdated_fields.items():
            if field == "modified_by":
                setattr(existing_organisation, "modifiedBy", value)
            else:
                setattr(existing_organisation, field, value)
        existing_organisation.modifiedDateTime = datetime.now(UTC)

    def _get_stored_organisation(
        self, organisation_id: str, ods_code: str
    ) -> Organisation | None:
        """
        Retrieve the stored organisation from the repository.
        """
        organisation = self.org_repository.get(organisation_id)
        if not organisation:
            self.logger.log(
                CrudApisLogBase.ORGANISATION_002,
                ods_code=ods_code,
            )
            outcome = OperationOutcomeHandler.build(
                diagnostics="Organisation not found.",
                code="not-found",
                severity="error",
            )
            raise OperationOutcomeException(outcome)
        return organisation

    def get_by_ods_code(self, ods_code: str) -> Organisation | None:
        """
        Retrieve the stored organisation from the repository by ODS code.
        """
        organisation = self.org_repository.get_by_ods_code(ods_code=ods_code)
        if not organisation:
            self.logger.log(
                CrudApisLogBase.ORGANISATION_002,
                ods_code=ods_code,
            )
            outcome = OperationOutcomeHandler.build(
                diagnostics=f"Organisation with ODS code '{ods_code}' not found",
                code="not-found",
                severity="error",
            )
            raise OperationOutcomeException(outcome)
        return organisation

    def check_organisation_params(self, params: dict) -> None:
        allowed = {"identifier"}
        extra = set(params.keys()) - allowed
        if extra:
            outcome = OperationOutcomeHandler.build(
                diagnostics=f"Unexpected query parameter(s): {', '.join(extra)}. Only 'identifier' is allowed.",
                code="invalid",
                severity="error",
            )
            raise OperationOutcomeException(outcome)

    def get_all_organisations(self, limit: int = 10) -> list[Organisation]:
        """
        Returns all Organisation objects from the repository.
        """
        self.logger.log(
            CrudApisLogBase.ORGANISATION_004,
        )
        organisations = list(self.org_repository.iter_records(max_results=limit))
        organisations = [
            org if isinstance(org, Organisation) else Organisation(**org)
            for org in organisations
        ]
        return organisations

    def _get_outdated_fields(
        self, organisation: Organisation, payload: Organisation
    ) -> dict:
        """
        Compare two Organisation objects and return a dict of fields that are outdated.
        Containing which fields can be updated for now will dedpend on business validation definitions.
        """
        allowed_fields = {
            "name",
            "type",
            "active",
            "telecom",
            "legalDates",
            "identifier_ODS_ODSCode",
            "primary_role_code",
            "non_primary_role_codes",
        }
        outdated_fields = {}

        for field, value in payload.model_dump().items():
            if field not in allowed_fields:
                continue

            existing_value = getattr(organisation, field, None)

            # Special handling for legalDates to compare start and end values
            if field == "legalDates":
                if self._legal_dates_differ(existing_value, value):
                    outdated_fields[field] = value
            elif field == "primary_role_code":
                if existing_value != value:
                    outdated_fields[field] = value
            elif field == "non_primary_role_codes":
                if set(existing_value or []) != set(value or []):
                    outdated_fields[field] = value
            elif existing_value != value:
                outdated_fields[field] = value

        if outdated_fields:
            self._validate_role_fields_if_changed(organisation, outdated_fields)
            self.logger.log(
                CrudApisLogBase.ORGANISATION_006,
                outdated_fields=list(outdated_fields.keys()),
                organisation_id=getattr(organisation, "id", None),
            )
            outdated_fields["modified_by"] = payload.modifiedBy or "ODS_ETL_PIPELINE"
            outdated_fields["modifiedDateTime"] = datetime.now(UTC)
        return outdated_fields

    def _legal_dates_differ(self, existing: LegalDates, new: LegalDates) -> bool:
        """Compare two legalDates to check if they differ."""
        if existing is None and new is None:
            return False
        if existing is None or new is None:
            return True

        existing_start = self._extract_date_field(existing, LegalDateField.START)
        existing_end = self._extract_date_field(existing, LegalDateField.END)
        new_start = self._extract_date_field(new, LegalDateField.START)
        new_end = self._extract_date_field(new, LegalDateField.END)

        return existing_start != new_start or existing_end != new_end

    def _extract_date_field(
        self, legal_dates: LegalDates, field: LegalDateField
    ) -> any:
        if not isinstance(field, LegalDateField):
            err_msg = "field must be a LegalDateField Enum value"
            raise TypeError(err_msg)
        key = field.value
        if hasattr(legal_dates, key):
            return getattr(legal_dates, key)
        if isinstance(legal_dates, dict):
            return legal_dates.get(key)
        return None

    def _validate_role_fields_if_changed(
        self, organisation: Organisation, outdated_fields: dict
    ) -> None:
        """Validate role combination if role fields have changed."""
        role_fields_changed = (
            "primary_role_code" in outdated_fields
            or "non_primary_role_codes" in outdated_fields
        )

        if not role_fields_changed:
            return

        primary_role = outdated_fields.get(
            "primary_role_code", organisation.primary_role_code
        )
        non_primary_roles = outdated_fields.get(
            "non_primary_role_codes", organisation.non_primary_role_codes or []
        )

        if isinstance(primary_role, str):
            try:
                primary_role = OrganisationTypeCode(primary_role)
                outdated_fields["primary_role_code"] = primary_role
            except ValueError:
                error_message = f"Invalid primary role code: '{primary_role}'. "
                self._handle_role_error(organisation.id, error_message)

        # Convert non-primary roles if they are strings
        if non_primary_roles and isinstance(non_primary_roles[0], str):
            try:
                converted_non_primary_roles = [
                    OrganisationTypeCode(role) for role in non_primary_roles
                ]
                outdated_fields["non_primary_role_codes"] = converted_non_primary_roles
                non_primary_roles = converted_non_primary_roles
            except ValueError as e:
                error_message = f"Invalid non-primary role code: {str(e)}. "
                self._handle_role_error(organisation.id, error_message)

        # Now validate the combination with enum values
        is_valid, error_message = validate_type_combination(
            primary_role, non_primary_roles
        )

        if not is_valid:
            self._handle_role_error(organisation.id, error_message)

    def _handle_role_error(self, organisation_id: str, error_message: str) -> None:
        """Log and raise exception for role related errors."""
        self.logger.log(
            CrudApisLogBase.ORGANISATION_023,
            organisation_id=organisation_id,
            error_message=error_message,
        )
        outcome = OperationOutcomeHandler.build(
            diagnostics=error_message,
            code="invalid",
            severity="error",
        )
        raise OperationOutcomeException(outcome)
