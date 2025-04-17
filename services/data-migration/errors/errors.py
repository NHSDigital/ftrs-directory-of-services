class InvalidArgumentsError(ValueError):
    def __init__(
        self,
        message: str = "Provide only one valid argument: either output path or S3 URI.",
    ) -> None:
        super().__init__(message)


class S3BucketAccessError(SystemExit):
    def __init__(self, bucket_uri: str, message: str = None) -> None:
        if message is None:
            message = (
                f"Bucket {bucket_uri} does not exist or you don't have access to it."
            )
        super().__init__(message)
