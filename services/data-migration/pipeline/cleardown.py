import logging
from enum import StrEnum

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
            err_msg = f"Unsupported entity type: {type}"
            raise ValueError(err_msg)


def cleardown(
    env: TargetEnvironment = Option(..., help="Environment to clear the data from"),
    workspace: str | None = Option(None, help="Workspace to clear the data from"),
    endpoint_url: str | None = Option(None, help="URL to connect to local DynamoDB"),
    entity_type: list[ClearableEntityTypes] = Option(
        DEFAULT_CLEARABLE_ENTITY_TYPES,
        help="Types of entities to clear from the database",
    ),
) -> None:
    """
    Reset the database by deleting all items in the specified table(s).
    This function is intended for use in development and local environments only.
    """
    if env not in [TargetEnvironment.dev, TargetEnvironment.local]:
        error_msg = f"Invalid environment: {env}. Only 'dev' and 'local' are allowed."
        logging.error(error_msg)
        raise ValueError(error_msg)

    if not confirm(
        f"Are you sure you want to clear the {env} environment? This action cannot be undone.",
        abort=True,
    ):
        logging.info("Cleardown operation aborted by user.")
        return

    for entity_name in entity_type:
        entity_cls = _get_entity_cls(entity_name)

        repository = DocumentLevelRepository[entity_cls](
            table_name=get_table_name(entity_name, env.value, workspace),
            model_cls=entity_cls,
            endpoint_url=endpoint_url,
        )

        for item in track(
            repository._iter_records(max_results=None),
            description=f"Deleting items from {entity_name}",
        ):
            repository.delete(item.id)
