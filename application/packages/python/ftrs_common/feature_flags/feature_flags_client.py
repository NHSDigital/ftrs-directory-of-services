import os
from functools import lru_cache
from typing import Protocol

from aws_lambda_powertools.utilities.feature_flags import AppConfigStore, FeatureFlags
from aws_lambda_powertools.utilities.feature_flags.exceptions import (
    ConfigurationStoreError,
)
from ftrs_common.feature_flags.feature_flag_config import FeatureFlag
from ftrs_common.logbase import FeatureFlagLogBase
from ftrs_common.logger import Logger
from ftrs_common.utils.config import Settings

logger = Logger.get(service="feature_flags")


# Cache TTL in seconds - matches AppConfig extension default poll interval
CACHE_TTL_SECONDS = 45


class FeatureFlagsClientProtocol(Protocol):
    """Protocol defining the interface for feature flag clients."""

    def is_enabled(self, flag_name: str, default: bool = False) -> bool:
        """Check if a feature flag is enabled."""
        ...


class LocalFlagsClient:
    """Local feature flags client for development and testing."""

    def __init__(self) -> None:
        self.flags: dict[str, bool] = {
            FeatureFlag.DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED.value: os.getenv(
                "DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED", "true"
            ).lower()
            == "true"
        }

    def is_enabled(self, flag_name: str, default: bool = False) -> bool:
        return self.flags.get(flag_name, default)


class FeatureFlagError(Exception):
    """Exception raised when feature flag evaluation fails."""

    def __init__(
        self, flag_name: str, message: str, original_exception: Exception | None = None
    ) -> None:
        self.flag_name = flag_name
        self.original_exception = original_exception
        super().__init__(f"Feature flag '{flag_name}' evaluation failed: {message}")


class FeatureFlagsClient:
    """Client for managing feature flags using AWS AppConfig."""

    _instance: "FeatureFlagsClient | None" = None
    _feature_flags: FeatureFlags | None = None

    def __new__(cls) -> "FeatureFlagsClient":
        """Singleton pattern to ensure a single instance with cached feature flags."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the FeatureFlagsClient with settings from the environment."""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.settings = Settings()
        self._initialized = True

    def _get_appconfig_store(self) -> AppConfigStore:
        """Create and return an AppConfigStore instance."""
        if not self.settings.appconfig_application_id:
            raise FeatureFlagError(
                flag_name="N/A",
                message="APPCONFIG_APPLICATION_ID environment variable is not set",
            )
        if not self.settings.appconfig_environment_id:
            raise FeatureFlagError(
                flag_name="N/A",
                message="APPCONFIG_ENVIRONMENT_ID environment variable is not set",
            )
        if not self.settings.appconfig_configuration_profile_id:
            raise FeatureFlagError(
                flag_name="N/A",
                message="APPCONFIG_CONFIGURATION_PROFILE_ID environment variable is not set",
            )

        logger.log(
            FeatureFlagLogBase.FF_001,
            application_id=self.settings.appconfig_application_id,
            environment_id=self.settings.appconfig_environment_id,
            configuration_profile_id=self.settings.appconfig_configuration_profile_id,
            cache_ttl_seconds=CACHE_TTL_SECONDS,
        )

        return AppConfigStore(
            application=self.settings.appconfig_application_id,
            environment=self.settings.appconfig_environment_id,
            name=self.settings.appconfig_configuration_profile_id,
            max_age=CACHE_TTL_SECONDS,
        )

    def get_feature_flags(self) -> FeatureFlags:
        if FeatureFlagsClient._feature_flags is None:
            store = self._get_appconfig_store()
            FeatureFlagsClient._feature_flags = FeatureFlags(store=store)
        return FeatureFlagsClient._feature_flags

    def is_enabled(
        self,
        flag_name: str,
        default: bool = False,
    ) -> bool:
        """Check if a feature flag is enabled."""
        try:
            feature_flags = self.get_feature_flags()
            store_config = feature_flags.store.get_configuration()

            if not store_config:
                flag_enabled = default
            elif flag_name not in store_config:
                # Flag doesn't exist, use default
                flag_enabled = default
                logger.log(
                    FeatureFlagLogBase.FF_005,
                    flag_name=flag_name,
                )
            else:
                # Read the enabled value directly from the flag config
                flag_config = store_config.get(flag_name, {})
                flag_enabled = flag_config.get("enabled", default)

            logger.log(
                FeatureFlagLogBase.FF_002,
                flag_name=flag_name,
                flag_enabled=flag_enabled,
            )

        except ConfigurationStoreError as e:
            logger.log(
                FeatureFlagLogBase.FF_003,
                flag_name=flag_name,
                exception=str(e),
            )
            raise FeatureFlagError(
                flag_name=flag_name,
                message="Configuration store error",
                original_exception=e,
            ) from e

        except Exception as e:
            logger.log(
                FeatureFlagLogBase.FF_004,
                flag_name=flag_name,
                exception=str(e),
            )
            raise FeatureFlagError(
                flag_name=flag_name,
                message=str(e),
                original_exception=e,
            ) from e

        else:
            return flag_enabled


@lru_cache(maxsize=1)
def _get_client() -> FeatureFlagsClientProtocol:
    """Get a cached feature flags client instance."""
    settings = Settings()
    if settings.env == "local" or (
        settings.env == "dev" and settings.workspace is not None
    ):
        return LocalFlagsClient()
    return FeatureFlagsClient()


def is_enabled(flag_name: str, default: bool = False) -> bool:
    """Check if a feature flag is enabled."""
    return _get_client().is_enabled(flag_name, default)
