from datetime import UTC, datetime

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.models import Organisation

from organisations.app.services.validators import UpdatePayloadValidator

crud_organisation_logger = Logger.get(service="crud_organisation_logger")


def get_outdated_fields(
    organisation: Organisation, payload: UpdatePayloadValidator
) -> dict:
    return {
        field: value
        for field, value in payload.model_dump().items()
        if (
            (
                field == "modified_by"
                and getattr(organisation, "modifiedBy", None) != value
            )
            or (field != "modified_by" and getattr(organisation, field, None) != value)
        )
    }


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
