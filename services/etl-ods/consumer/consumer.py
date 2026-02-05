import requests
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.apim_client import make_apim_request
from common.error_handling import handle_http_error
from common.sqs_processor import (
    create_sqs_lambda_handler,
    extract_record_metadata,
    validate_required_fields,
)
from common.url_config import get_base_apim_api_url

ods_consumer_logger = Logger.get(service="ods_consumer")


def process_message_and_send_request(record: dict) -> None:
    metadata = extract_record_metadata(record)
    body_content = metadata["body"]
    message_id = metadata["message_id"]

    validate_required_fields(
        body_content, ["path", "body"], message_id, ods_consumer_logger
    )

    path = body_content.get("path")
    body = body_content.get("body")

    api_url = get_base_apim_api_url()
    organization_id = path
    api_url = api_url + "/Organization/" + organization_id

    try:
        response_data = make_apim_request(api_url, method="PUT", json=body)
        ods_consumer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_007,
            organization_id=organization_id,
            status_code=response_data.get("status_code", "unknown"),
        )
    except requests.exceptions.HTTPError as http_error:
        handle_http_error(http_error, message_id, "consumer_organization_put_request")


consumer_lambda_handler = create_sqs_lambda_handler(
    process_function=process_message_and_send_request,
    logger=ods_consumer_logger,
)
