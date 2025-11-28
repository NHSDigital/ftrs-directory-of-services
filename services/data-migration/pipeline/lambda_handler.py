from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger

from pipeline.application import DataMigrationApplication

APP: DataMigrationApplication | None = None
LOGGER = Logger.get(service="data-migration")


@event_source(data_class=SQSEvent)
@LOGGER.inject_lambda_context
def lambda_handler(event: SQSEvent, context: LambdaContext) -> None:
    """
    AWS Lambda entrypoint for transforming data.
    This function will be triggered by an SQS event containing a batch of DMS events.
    """
    global APP  # noqa: PLW0603
    if APP is None:
        APP = DataMigrationApplication()

    APP.handle_sqs_event(event)
