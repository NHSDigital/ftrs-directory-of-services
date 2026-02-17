import os

from ftrs_common.utils.jwt_auth import JWTAuthenticator

_jwt_authenticator: JWTAuthenticator = None


def get_jwt_authenticator() -> JWTAuthenticator:
    """Get JWT authenticator instance, using cached instance if available."""
    global _jwt_authenticator  # noqa: PLW0603

    if _jwt_authenticator is None:
        print("Creating new JWTAuthenticator instance")
        environment = os.environ.get("ENVIRONMENT", "local")
        resource_prefix = get_resource_prefix()

        _jwt_authenticator = JWTAuthenticator(
            environment=environment,
            region=os.environ["AWS_REGION"],
            secret_name=f"/{resource_prefix}/dos-ingest-jwt-credentials",
        )

    return _jwt_authenticator


def get_resource_prefix() -> str:
    project = os.environ.get("PROJECT_NAME")
    environment = os.environ.get("ENVIRONMENT")
    return f"{project}/{environment}"
