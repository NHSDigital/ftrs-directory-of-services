from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from functions.logging.dos_logger import DosLogger

logger = Logger()

dos_logger = DosLogger.get(service="test_logger")


@logger.inject_lambda_context(
    log_event=True,
    clear_state=True,
)
def lambda_handler(
    event: dict,
    context: LambdaContext,
    function: Any,
) -> any:
    dos_logger.init(event)
    return function()
