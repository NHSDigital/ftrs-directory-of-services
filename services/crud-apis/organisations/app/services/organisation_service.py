from builtins import ValueError, dict, isinstance
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
from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from pydantic import ValidationError


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
        nhse_product_id: str | None = None,
    ) -> bool:
        """
        Update an organisation from a FHIR Organisation resource.
        """
        lastUpdatedBy = AuditEvent(
            type=AuditEventType.app, value="", display="Data Management"
        )

        if nhse_product_id:
            lastUpdatedBy.value = nhse_product_id
            lastUpdatedBy.display = "ODS"
        try:
            fhir_organisation = FhirValidator.validate(fhir_org, FhirOrganisation)
            ods_code = None

            if (
                hasattr(fhir_org, "identifier")
                and fhir_org.identifier
                and hasattr(fhir_org.identifier[0], "value")
            ):
                ods_code = fhir_org.identifier[0].value
            stored_organisation = self._get_stored_organisation(
                organisation_id, ods_code
            )
            organisation = self.organisation_mapper.from_fhir(fhir_organisation)
            organisation.lastUpdatedBy = lastUpdatedBy
            outdated_fields = self._get_outdated_fields(
                stored_organisation, organisation
            )

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
        except (ValidationError, ValueError) as e:
            self._handle_validation_errors(organisation_id, e)
            raise
        return True

    def _handle_validation_errors(self, organisation_id: str, e: Exception) -> None:
        """
        Handle validation errors by raising an OperationOutcomeException.
        """
        if isinstance(e, ValidationError):
            self.logger.log(
                CrudApisLogBase.ORGANISATION_019,
                organisation_id=organisation_id,
                status_code=422,
                error_message=str(e),
            )
            diagnostics = []
            for error in e.errors():
                if isinstance(error["input"], dict) and "type" in error["input"].keys():
                    if "phone" in error["input"]["type"]:
                        diagnostics.append(
                            f"Telecom value field contains an invalid phone number: {error['input']['value']}"
                        )
                    elif "email" in error["input"]["type"]:
                        diagnostics.append(
                            f"Telecom value field contains an invalid email address: {error['input']['value']}"
                        )
                elif "url" in error["type"]:
                    diagnostics.append(
                        f"Telecom value field contains an invalid url: {error['input']}"
                    )
                elif "string_type" in error["type"]:
                    diagnostics.append(
                        f"'{error['loc'][0]}' field {error['msg'].lower()}"
                    )
                else:
                    diagnostics.append(f"Unexpected validation error: {error['msg']}")
            outcome = OperationOutcomeHandler.build(
                diagnostics=f"Validation failed for the following resources: {'; '.join(diagnostics)}",
                code="invalid",
                severity="error",
            )
            raise OperationOutcomeException(outcome) from e
        elif isinstance(e, ValueError):
            self.logger.log(
                CrudApisLogBase.ORGANISATION_019,
                organisation_id=organisation_id,
                error_message=str(e),
            )
            outcome = OperationOutcomeHandler.build(
                diagnostics=f"Validation failed for the following resource: {str(e)}",
                code="invalid",
                severity="error",
            )
            raise OperationOutcomeException(outcome) from e

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
            setattr(existing_organisation, field, value)

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
        Containing which fields can be updated for now will depend on business validation definitions.
        """
        allowed_fields = {
            "name",
            "active",
            "telecom",
            "legalDates",
            "identifier_ODS_ODSCode",
            "primary_role_code",
            "non_primary_role_codes",
        }

        current = {field: getattr(organisation, field) for field in allowed_fields}
        new = {field: getattr(payload, field) for field in allowed_fields}

        outdated_fields = {}

        for field in allowed_fields:
            if self._field_has_changed(current[field], new[field]):
                outdated_fields[field] = getattr(payload, field)

        if outdated_fields:
            self.logger.log(
                CrudApisLogBase.ORGANISATION_006,
                outdated_fields=list(outdated_fields.keys()),
                organisation_id=getattr(organisation, "id", None),
            )
            outdated_fields["lastUpdatedBy"] = payload.lastUpdatedBy
            outdated_fields["lastUpdated"] = datetime.now(UTC)
        return outdated_fields

    def _field_has_changed(self, current_value: object, new_value: object) -> bool:
        return current_value != new_value
