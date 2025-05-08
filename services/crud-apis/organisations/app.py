import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import Body, Depends, FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from ftrs_data_layer.models import Organisation
from ftrs_data_layer.repository.dynamodb import (
    DocumentLevelRepository,
)

from organisations.dependencies import get_app_settings
from organisations.settings import AppSettings
from organisations.validators import UpdatePayloadValidator

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)


@app.put("/{organisation_id}", summary="Update an organisation.")
def update_organisation(
    organisation_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The internal id of the organisation",
    ),
    payload: UpdatePayloadValidator = Body(...),
    settings: AppSettings = Depends(get_app_settings),
) -> dict:
    logging.info(f"Received request to update organisation with ID: {organisation_id}")

    org_repository = get_repository(
        env=settings.env,
        workspace=settings.workspace,
        endpoint_url=settings.endpoint_url,
    )

    existing_organisation = org_repository.get(organisation_id)

    if not existing_organisation:
        logging.info(f"Organisation with ID {organisation_id} not found.")
        raise HTTPException(status_code=404, detail="Organisation not found")

    outdated_fields = get_outdated_fields(existing_organisation, payload)
    logging.info(
        f"Computed outdated fields: {outdated_fields} for organisation {organisation_id}"
    )

    if not outdated_fields:
        logging.info(f"No changes detected for organisation {organisation_id}.")
        return JSONResponse(status_code=200, content={"message": "No changes detected"})

    apply_updates(existing_organisation, outdated_fields)
    org_repository.update(id, existing_organisation)
    logging.info(f"Successfully updated organisation {organisation_id}")

    return JSONResponse(
        status_code=200, content={"message": "Data processed successfully"}
    )


def get_table_name(entity_type: str, env: str, workspace: str | None = None) -> str:
    """
    Build a DynamoDB table name based on the entity type, environment, and optional workspace.
    """
    table_name = f"ftrs-dos-{env}-database-{entity_type}"
    if workspace:
        table_name = f"{table_name}-{workspace}"

    return table_name


def get_repository(
    env: str = "local",
    workspace: str | None = None,
    endpoint_url: str | None = None,
) -> DocumentLevelRepository[Organisation]:
    return DocumentLevelRepository[Organisation](
        table_name=get_table_name("organisation", env, workspace),
        model_cls=Organisation,
        endpoint_url=endpoint_url,
    )


def get_outdated_fields(
    organisation: Organisation, payload: UpdatePayloadValidator
) -> dict:
    return {
        field: value
        for field, value in payload.model_dump().items()
        if getattr(organisation, field, None) != value
    }


def apply_updates(
    existing_organisation: Organisation, outdated_fields: dict
) -> Organisation:
    logging.info(f"Applying updates to organisation: {existing_organisation.id}")
    for field, value in outdated_fields.items():
        setattr(existing_organisation, field, value)
    existing_organisation.modifiedBy = "ROBOT_API"
    existing_organisation.modifiedDateTime = datetime.now(UTC)
