import os

from ftrs_common.utils.jwt_auth import JWTAuthenticator


def get_jwt_authenticator() -> JWTAuthenticator:
    environment = os.environ.get("ENVIRONMENT", "local")
    project = os.environ.get("PROJECT_NAME")

    return JWTAuthenticator(
        environment=environment,
        region=os.environ["AWS_REGION"],
        secret_name=f"/{project}/internal-qa/dos-ingest-jwt-credentials",
    )
