"""
Configuration settings for the application.
"""

import os
from typing import Dict


class MissingEnvironmentVariable(Exception):
    """Exception raised when environment variable is missing"""

    def __init__(self, var_name: str) -> None:
        self.message = f"Required environment variable '{var_name}' is not set"
        super().__init__(self.message)


def get_config() -> Dict[str, str]:
    """
    Get configuration settings from environment variables.

    Returns:
        Dictionary of configuration settings

    Raises:
        MissingEnvironmentVariable if required variable not set
    """
    config = {
        "DYNAMODB_TABLE_NAME": _get_env_var("DYNAMODB_TABLE_NAME"),
        "FHIR_BASE_URL": _get_env_var("FHIR_BASE_URL", "https://example.org"),
        "LOG_LEVEL": _get_env_var("LOG_LEVEL", "INFO"),
    }
    return config


def _get_env_var(var_name: str, default: str = None) -> str:
    """
    Get environment variable value or raise exception if not set.

    Args:
        var_name: Name of environment variable
        default: Optional default value if not set

    Returns:
        Environment variable value

    Raises:
        MissingEnvironmentVariable if variable not set and no default provided
    """
    value = os.environ.get(var_name, default)
    if value is None:
        raise MissingEnvironmentVariable(var_name)
    return value
