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
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.models import Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository


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

    def _get_outdated_fields(
        self, organisation: Organisation, payload: Organisation
    ) -> dict:
        """
        Compare two Organisation objects and return a dict of fields that are outdated.
        """
        outdated_fields = {
            field: value
            for field, value in payload.model_dump().items()
            if (
                (
                    field == "modified_by"
                    and getattr(organisation, "modifiedBy", None) != value
                )
                or (
                    field != "modified_by"
                    and getattr(organisation, field, None) != value
                )
            )
        }
        if outdated_fields:
            self.logger.log(
                CrudApisLogBase.ORGANISATION_006,
                outdated_fields=outdated_fields,
                organisation_id=getattr(organisation, "id", None),
            )
        return outdated_fields
