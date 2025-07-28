from pipeline.application import DataMigrationApplication


def lambda_handler(event: dict, context: dict) -> None:
    """
    AWS Lambda entrypoint for transforming data.
    This function will be triggered by an S3 event.
    """
    app = DataMigrationApplication()
    return app.handle_event(event)
