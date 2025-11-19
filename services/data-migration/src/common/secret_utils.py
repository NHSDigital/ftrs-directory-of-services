import os

from aws_lambda_powertools.utilities import parameters
from dotenv import load_dotenv


def get_secret(secret_name: str, transform: str | None = None) -> str:
    load_dotenv()
    environment = os.getenv("ENVIRONMENT")
    project_name = os.getenv("PROJECT_NAME")

    if not environment or not project_name:
        raise ValueError(
            "Missing required environment variables: ENVIRONMENT and/or PROJECT_NAME"
        )

    return parameters.get_secret(
        name=f"/{project_name}/{environment}/{secret_name}",
        transform=transform,
    )
