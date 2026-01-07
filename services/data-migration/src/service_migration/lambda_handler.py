from aws_lambda_powertools.utilities.batch.types import PartialItemFailureResponse
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger

from service_migration.application import ServiceMigrationApplication

APP: ServiceMigrationApplication | None = None
LOGGER = Logger.get(service="data-migration")


@LOGGER.inject_lambda_context
def lambda_handler(
    event: dict,
    context: LambdaContext,
) -> PartialItemFailureResponse:
    """
    AWS Lambda entrypoint for transforming data.
    This function will be triggered by an SQS event containing a batch of DMS events.
    """
    global APP  # noqa: PLW0603
    if APP is None:
        APP = ServiceMigrationApplication()

    return APP.handle_sqs_event(event, context)
