class InvalidS3URI(Exception):
    """Invalid S3 URI exception"""

    def __init__(self, uri: str = "uri") -> None:
        self.uri = uri
        super().__init__(f"Invalid S3 URI: {self.uri}")


class ExtractArgsError(Exception):
    """Extract arguments error exception"""
