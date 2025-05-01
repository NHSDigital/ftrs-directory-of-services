import os

from aws_lambda_powertools.utilities import parameters
from dotenv import load_dotenv


# TODO: udpate as part of FDOS-197
class MissingEnvironmentOrProjectNameError(Exception):
    """Exception raised when the environment or project name is missing."""

    def __init__(
        self, message: str = "The environment or project name does not exist"
    ) -> None:
        self.message = message
        super().__init__(self.message)


def get_secret(secret_name: str, transform: str | None = None) -> str:
    load_dotenv()
    environment = os.getenv("ENVIRONMENT")
    project_name = os.getenv("PROJECT_NAME")

    if not environment or not project_name:
        raise MissingEnvironmentOrProjectNameError

    return parameters.get_secret(
        name=f"/{project_name}/{environment}/{secret_name}", transform=transform
    )
