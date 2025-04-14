import logging
from enum import StrEnum
from typing import Annotated

from ftrs_data_layer.models import HealthcareService, Location, Organisation
from ftrs_data_layer.repository.dynamodb import (
    DocumentLevelRepository,
    ModelType,
)
from rich.progress import track
from typer import Option, confirm

from pipeline.common import TargetEnvironment, get_table_name


class ClearableEntityTypes(StrEnum):
    organisation = "organisation"
    healthcare_service = "healthcare-service"
    location = "location"


class RepositoryTypes(StrEnum):
    document = "document"
    field = "field"


DEFAULT_CLEARABLE_ENTITY_TYPES = [
    ClearableEntityTypes.organisation,
    ClearableEntityTypes.healthcare_service,
    ClearableEntityTypes.location,
]


def _get_entity_cls(entity_type: ClearableEntityTypes) -> ModelType:
    """
    Map entity types to their corresponding classes.
    """
    match entity_type:
        case ClearableEntityTypes.organisation:
            return Organisation
        case ClearableEntityTypes.healthcare_service:
            return HealthcareService
        case ClearableEntityTypes.location:
            return Location
        case _:
            err_msg = f"Unsupported entity type: {entity_type}"
            raise ValueError(err_msg)


def cleardown(
    env: Annotated[
        TargetEnvironment, Option(..., help="Environment to clear the data from")
    ],
    workspace: Annotated[
        str | None, Option(..., help="Workspace to clear the data from")
    ] = None,
    endpoint_url: Annotated[
        str | None, Option(..., help="URL to connect to local DynamoDB")
    ] = None,
    entity_type: Annotated[
        list[ClearableEntityTypes] | None,
        Option(
            None,
            help="Types of entities to clear from the database",
        ),
    ] = None,
) -> None:
    """
    Reset the database by deleting all items in the specified table(s).
    This function is intended for use in development and local environments only.
    """
    if entity_type is None:
        entity_type = DEFAULT_CLEARABLE_ENTITY_TYPES

    if env not in [TargetEnvironment.dev, TargetEnvironment.local]:
        error_msg = f"Invalid environment: {env}. Only 'dev' and 'local' are allowed."
        logging.error(error_msg)
        raise ValueError(error_msg)

    confirm(
        f"Are you sure you want to clear the {env} environment? This action cannot be undone.",
        abort=True,
    )

    for entity_name in entity_type:
        entity_cls = _get_entity_cls(entity_name)

        repository = DocumentLevelRepository(
            table_name=get_table_name(entity_name, env.value, workspace),
            model_cls=entity_cls,
            endpoint_url=endpoint_url,
        )

        for item in track(
            repository.iter_records(max_results=None),
            description=f"Deleting items from {entity_name}",
        ):
            repository.delete(item.id)
