from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.event_handler.middlewares import NextMiddleware
from ftrs_common.logger import Logger

from functions.event_context import setup_request

logger = Logger.get(service="dos-search")


def request_context_middleware(
    app: APIGatewayRestResolver, next_middleware: NextMiddleware
) -> Response:
    setup_request(app.current_event, logger)
    try:
        return next_middleware(app)
    finally:
        logger.thread_safe_clear_keys()
