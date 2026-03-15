"""Feature flags module for ftrs_common.

This module provides utilities for feature flag management using AWS AppConfig
and AWS Lambda Powertools.

Usage:
    from ftrs_common.feature_flags import FeatureFlagsClient

    # Using the client class
    client = FeatureFlagsClient()
    if client.is_enabled("my_feature"):
        # Feature is enabled
        pass

    # Or using convenience functions
    from ftrs_common.feature_flags import is_enabled

    if is_enabled("my_feature", default=True):
        pass
"""

from ftrs_common.feature_flags.feature_flag_config import FeatureFlag
from ftrs_common.feature_flags.feature_flags_client import (
    FeatureFlagError,
    FeatureFlagsClient,
    is_enabled,
)

from .feature_flag_handlers import (
    FeatureFlagGuardConfig,
    FeatureFlagGuardDependencies,
    RequestGuard,
    RequestGuardChain,
    build_feature_flag_guard,
    build_feature_flag_guard_chain,
)

type FeatureFlagExports = list[str]

__all__: FeatureFlagExports = [
    "FeatureFlagError",
    "FeatureFlag",
    "FeatureFlagsClient",
    "FeatureFlagGuardConfig",
    "FeatureFlagGuardDependencies",
    "RequestGuard",
    "RequestGuardChain",
    "build_feature_flag_guard",
    "build_feature_flag_guard_chain",
    "is_enabled",
]
