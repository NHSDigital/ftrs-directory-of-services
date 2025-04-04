class InvalidS3URI(Exception):
    """Invalid S3 URI exception"""

    def __init__(self, message: str = "Invalid S3 URI") -> None:
        self.message = message
        super().__init__(self.message)


class S3BucketAccessError(Exception):
    """S3 bucket access error exception"""

    def __init__(self, message: str = "Error accessing S3 bucket") -> None:
        self.message = message
        super().__init__(self.message)


class ExtractArgsError(Exception):
    """Extract arguments error exception"""

    def __init__(self, message: str = "Error with the number of arguments") -> None:
        self.message = message
        super().__init__(self.message)
