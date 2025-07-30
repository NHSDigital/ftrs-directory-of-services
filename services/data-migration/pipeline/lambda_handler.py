from pipeline.application import DataMigrationApplication

APP: DataMigrationApplication | None = None


def lambda_handler(event: dict, context: dict) -> None:
    """
    AWS Lambda entrypoint for transforming data.
    This function will be triggered by an S3 event.
    """
    global APP  # noqa: PLW0603
    if APP is None:
        APP = DataMigrationApplication()

    return APP.handle_event(event)
