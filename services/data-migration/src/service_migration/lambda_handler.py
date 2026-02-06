from aws_lambda_powertools.utilities.batch.types import PartialItemFailureResponse
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.feature_flags import FeatureFlagsClient
from ftrs_common.logger import Logger

from service_migration.application import DataMigrationApplication

APP: DataMigrationApplication | None = None
LOGGER = Logger.get(service="data-migration")

# Initialize AppConfig client in init state
FEATURE_FLAGS_CLIENT: FeatureFlagsClient = FeatureFlagsClient()


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
        APP = DataMigrationApplication()

    return APP.handle_sqs_event(event, context)
