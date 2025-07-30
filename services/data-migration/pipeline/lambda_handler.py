from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source

from pipeline.application import DataMigrationApplication

APP: DataMigrationApplication | None = None


@event_source(data_class=SQSEvent)
def lambda_handler(event: SQSEvent, context: dict) -> None:
    """
    AWS Lambda entrypoint for transforming data.
    This function will be triggered by an S3 event.
    """
    global APP  # noqa: PLW0603
    if APP is None:
        APP = DataMigrationApplication()

    APP.handle_sqs_event(event)
