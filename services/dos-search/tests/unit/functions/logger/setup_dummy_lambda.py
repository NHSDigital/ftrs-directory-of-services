from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext

from functions.logger.dos_logger import DosLogger

dos_logger = DosLogger.get(service="test_logger")
logger = dos_logger._logger


@logger.inject_lambda_context(
    log_event=True,
    clear_state=True,
)
def lambda_handler(
    event: dict,
    context: LambdaContext,
    function: Any,
    *,
    run_init: bool = True,
) -> any:
    if run_init:
        dos_logger.init(event)
    return function()
