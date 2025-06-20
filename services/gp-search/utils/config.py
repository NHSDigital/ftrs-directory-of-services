from os import environ


class EnvironmentVariableNotFoundError(Exception):
    def __init__(self, var_name: str) -> None:
        self.message = f"Required environment variable '{var_name}' is not set"
        super().__init__(self.message)


def get_config() -> dict[str, str]:
    config = {
        "DYNAMODB_TABLE_NAME": _get_env_var("DYNAMODB_TABLE_NAME"),
        "FHIR_BASE_URL": _get_env_var("FHIR_BASE_URL", "https://example.org"),
    }
    return config


def _get_env_var(var_name: str, default: str = None) -> str:
    value = environ.get(var_name, default)
    if value is None:
        raise EnvironmentVariableNotFoundError(var_name)
    return value
