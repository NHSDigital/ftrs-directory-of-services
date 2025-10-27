from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger

from common.events import ReferenceDataLoadEvent
from reference_data_load.application import ReferenceDataLoadApplication

APP: ReferenceDataLoadApplication | None = None
LOGGER = Logger.get(service="reference-data-load")


@LOGGER.inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext) -> None:
    """
    AWS Lambda entrypoint for transforming data.
    This function will be triggered by an SQS event containing a batch of DMS events.
    """
    global APP  # noqa: PLW0603
    if APP is None:
        APP = ReferenceDataLoadApplication()

    APP.handle(ReferenceDataLoadEvent(**event))
