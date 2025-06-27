from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException
from ftrs_common.fhir.operation_outcome import OperationOutcomeException, OperationOutcomeHandler
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.models import DBModel, Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

from fastapi.responses import JSONResponse
from fhir.resources.R4B.organization import Organization

from common.fhir.r4b.organization_mapper import OrganizationMapper

crud_organisation_logger = Logger.get(service="crud_organisation_logger")
organisation_mapper = OrganizationMapper()

class OrganisationService:
    def __init__(self, org_repository, logger):
        self.org_repository = org_repository
        self.logger = logger

    def process_organisation_update(
        self, organisation_id, fhir_org,
    ):
        fhir_organisation = Organization.model_validate(fhir_org)

        ods_code = fhir_org.get("identifier", [{}])[0].get("value") if isinstance(fhir_org.get("identifier"), list) else None
        stored_organisation = self.get_stored_organisation(organisation_id, ods_code)

        organisation = organisation_mapper.from_fhir(fhir_organisation)

        outdated_fields = self.get_outdated_fields(stored_organisation, organisation)

        if not outdated_fields:
            self.logger.log(
                CrudApisLogBase.ORGANISATION_007,
                organisation_id=organisation_id,
            )
            return JSONResponse(status_code=200, content={"message": "No changes detected"})

        self.apply_updates(organisation, outdated_fields)
        self.org_repository.update(organisation_id, organisation)
        self.logger.log(
            CrudApisLogBase.ORGANISATION_008,
            organisation_id=organisation_id,
        )

        return JSONResponse(
            status_code=200, content={"message": "Data processed successfully"}
        )

def apply_updates(
    existing_organisation: Organisation, outdated_fields: dict
) -> Organisation:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_009,
        organisation_id=existing_organisation.id,
    )
    for field, value in outdated_fields.items():
        if field == "modified_by":
            setattr(existing_organisation, "modifiedBy", value)
        else:
            setattr(existing_organisation, field, value)
    existing_organisation.modifiedDateTime = datetime.now(UTC)


def create_organisation(
    organisation: Organisation, org_repository: AttributeLevelRepository[DBModel]
) -> Organisation:
    # if the organisation already exists, we log it and raise an error
    existing_organisation = org_repository.get_by_ods_code(
        organisation.identifier_ODS_ODSCode
    )
    if existing_organisation:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_013,
            ods_code=organisation.identifier_ODS_ODSCode,
        )
        raise HTTPException(
            status_code=409, detail="Organisation with this ODS code already exists"
        )
    # If the organisation already has an ID, we log it and generate a new one
    if organisation.id is not None:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_014,
            organisation_id=organisation.id,
        )
        organisation.id = uuid4()
    org_repository.create(organisation)
    return organisation
    def get_stored_organisation(self, organisation_id: str, ods_code: str) -> Organisation | None:
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
                status_code=404,
            )
            raise OperationOutcomeException(outcome)
        return organisation

    def get_outdated_fields(
        self, organisation: Organisation, payload: Organisation
    ) -> dict:
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

    def apply_updates(
        self, existing_organisation: Organisation, outdated_fields: dict
    ) -> Organisation:
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
        return existing_organisation
