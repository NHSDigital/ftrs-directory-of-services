import os

from ftrs_common.utils.jwt_auth import JWTAuthenticator

from .secrets import SecretManager

_jwt_authenticator: JWTAuthenticator = None


def get_jwt_authenticator() -> JWTAuthenticator:
    """Get JWT authenticator instance, using cached instance if available."""
    global _jwt_authenticator  # noqa: PLW0603

    if _jwt_authenticator is None:
        environment = os.environ.get("ENVIRONMENT", "local")
        resource_prefix = SecretManager.get_resource_prefix()

        _jwt_authenticator = JWTAuthenticator(
            environment=environment,
            region=os.environ["AWS_REGION"],
            secret_name=f"/{resource_prefix}/dos-ingest-jwt-credentials",
        )

    return _jwt_authenticator
