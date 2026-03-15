"""Utilities for building feature-flag guards around request handlers."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from ftrs_common.feature_flags.feature_flag_config import FeatureFlag
from ftrs_common.feature_flags.feature_flags_client import is_enabled
from ftrs_common.logger import LogBase, Logger

type LogContext = Mapping[str, object]
type ErrorResourceFactory[ResourceT] = Callable[[], ResourceT]
type ResponseSizeAndDurationCalculator[ResourceT] = Callable[
    [ResourceT, float, Logger], tuple[int, int]
]
type ResponseFactory[ResourceT, ResponseT] = Callable[[int, ResourceT], ResponseT]


class RequestGuard[ArgumentT, ResponseT](Protocol):
    def __call__(self, request_arg: ArgumentT) -> ResponseT | None: ...


class RequestGuardChain[ArgumentT, ResponseT]:
    def __init__(
        self,
        guards: Sequence[RequestGuard[ArgumentT, ResponseT]],
        handler: Callable[[ArgumentT], ResponseT],
    ) -> None:
        self._guards = tuple(guards)
        self._handler = handler

    def handle(self, request_arg: ArgumentT) -> ResponseT:
        for guard in self._guards:
            response = guard(request_arg)
            if response is not None:
                return response
        return self._handler(request_arg)


@dataclass(frozen=True)
class FeatureFlagGuardConfig:
    flag_name: FeatureFlag | str
    enabled_log_reference: LogBase
    disabled_log_reference: LogBase
    log_context: LogContext | None = None
    status_code: int = 503
    default: bool = False


@dataclass(frozen=True)
class FeatureFlagGuardDependencies[ResourceT, ResponseT]:
    logger_getter: Callable[[], Logger]
    create_error_resource_getter: Callable[[], ErrorResourceFactory[ResourceT]]
    get_response_size_and_duration_getter: Callable[
        [], ResponseSizeAndDurationCalculator[ResourceT]
    ]
    create_response_getter: Callable[[], ResponseFactory[ResourceT, ResponseT]]


def _resolve_flag_config_name(flag_name: FeatureFlag | str) -> str:
    """Return the AppConfig lookup key for a feature flag."""

    return flag_name.value if isinstance(flag_name, FeatureFlag) else flag_name


def _resolve_flag_log_name(flag_name: FeatureFlag | str) -> str:
    """Return the human-readable/loggable name for a feature flag."""

    return flag_name.name if isinstance(flag_name, FeatureFlag) else flag_name


def _create_disabled_feature_flag_response[ResourceT, ResponseT](
    *,
    start: float,
    config: FeatureFlagGuardConfig,
    dependencies: FeatureFlagGuardDependencies[ResourceT, ResponseT],
    logger: Logger,
) -> ResponseT:
    flag_log_name = _resolve_flag_log_name(config.flag_name)
    log_context = config.log_context or {}
    create_error_resource = dependencies.create_error_resource_getter()
    calculate_response_size_and_duration = (
        dependencies.get_response_size_and_duration_getter()
    )
    create_response = dependencies.create_response_getter()

    error_resource = create_error_resource()
    response_size, duration_ms = calculate_response_size_and_duration(
        error_resource, start, logger
    )
    logger.log(
        config.disabled_log_reference,
        feature_flag=flag_log_name,
        feature_flag_status="disabled",
        dos_response_time=f"{duration_ms}ms",
        dos_response_size=response_size,
        **log_context,
    )
    return create_response(config.status_code, error_resource)


def build_feature_flag_guard[ResourceT, ResponseT](
    *,
    config: FeatureFlagGuardConfig,
    dependencies: FeatureFlagGuardDependencies[ResourceT, ResponseT],
) -> RequestGuard[float, ResponseT]:
    flag_log_name = _resolve_flag_log_name(config.flag_name)
    flag_config_name = _resolve_flag_config_name(config.flag_name)
    log_context = config.log_context or {}

    def _guard_request(start: float) -> ResponseT | None:
        logger = dependencies.logger_getter()

        if is_enabled(flag_config_name, config.default):
            logger.log(
                config.enabled_log_reference,
                feature_flag=flag_log_name,
                feature_flag_status="enabled",
                **log_context,
            )
            return None

        return _create_disabled_feature_flag_response(
            start=start,
            config=config,
            dependencies=dependencies,
            logger=logger,
        )

    return _guard_request


def build_feature_flag_guard_chain[ResourceT, ResponseT](
    *,
    config: FeatureFlagGuardConfig,
    dependencies: FeatureFlagGuardDependencies[ResourceT, ResponseT],
    handler: Callable[[float], ResponseT],
    additional_guards: Sequence[RequestGuard[float, ResponseT]] = (),
) -> RequestGuardChain[float, ResponseT]:
    request_guard = build_feature_flag_guard(
        config=config,
        dependencies=dependencies,
    )
    return RequestGuardChain(
        guards=[request_guard, *additional_guards],
        handler=handler,
    )


__all__ = [
    "RequestGuard",
    "RequestGuardChain",
    "FeatureFlagGuardConfig",
    "FeatureFlagGuardDependencies",
    "build_feature_flag_guard",
    "build_feature_flag_guard_chain",
    "_resolve_flag_config_name",
]
