from aws_lambda_powertools.utilities.typing import LambdaContext
from dos_ingest.app import app
from dos_ingest.logging import logger
from ftrs_common.utils.request_id import fetch_or_set_request_id
from mangum import Mangum


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> dict:
    fetch_or_set_request_id(
        context_id=getattr(context, "aws_request_id", None) if context else None,
        header_id=event.get("headers", {}).get("X-Request-ID"),
    )

    mangum_handler = Mangum(app, lifespan="off")
    return mangum_handler(event, context)
