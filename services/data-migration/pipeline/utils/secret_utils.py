import os

from aws_lambda_powertools.utilities.parameters import get_parameters


def get_dms_workspaces() -> list[str]:
    ssm_path = os.environ.get("SQS_SSM_PATH")
    if not ssm_path:
        raise ValueError("Missing required environment variable: SQS_SSM_PATH")

    params = get_parameters(
        ssm_path,
        recursive=True,
        decrypt=True,
        max_age=300,  # cache TTL = 300 seconds (5 minutes)
    )
    workspaces = list(params.values())
    return workspaces
