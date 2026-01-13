import json
import os

import boto3
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import get_correlation_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

ods_processor_logger = Logger.get(service="ods_processor")


def get_queue_name(env: str, workspace: str | None = None) -> str:
    """
    Gets an SQS queue name based on the environment, and optional workspace.
    """
    queue_name = f"ftrs-dos-{env}-etl-ods-queue"
    if workspace:
        queue_name = f"{queue_name}-{workspace}"
    return queue_name


def get_queue_url(queue_name: str, sqs: any) -> any:
    """
    Gets an SQS queue url based on the queue name.
    """
    try:
        return sqs.get_queue_url(QueueName=queue_name)
    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_013,
            queue_name=queue_name,
            error_message=str(e),
        )
        raise


def load_data(transformed_data: list[str]) -> None:
    try:
        correlation_id = get_correlation_id()
        if correlation_id:
            ods_processor_logger.append_keys(correlation_id=correlation_id)

        batch = []
        for index, item in enumerate(transformed_data, start=1):
            batch.append({"Id": str(index), "MessageBody": json.dumps(item)})
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_014,
            number=len(transformed_data),
        )

        sqs = boto3.client("sqs", region_name=os.environ["AWS_REGION"])
        queue_name = get_queue_name(os.environ["ENVIRONMENT"], os.environ["WORKSPACE"])
        response_get_queue = get_queue_url(queue_name, sqs)

        queue_url = response_get_queue["QueueUrl"]

        response = sqs.send_message_batch(QueueUrl=queue_url, Entries=batch)

        successful = len(response.get("Successful", []))
        failed = len(response.get("Failed", []))

        if failed > 0:
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_015,
                failed=failed,
            )

            for fail in response.get("Failed", []):
                ods_processor_logger.log(
                    OdsETLPipelineLogBase.ETL_PROCESSOR_016,
                    id=fail.get("Id"),
                    message=fail.get("Message"),
                    code=fail.get("Code"),
                )
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_017,
            successful=successful,
        )
    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_018,
            error_message=str(e),
        )
        raise
