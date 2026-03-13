from collections.abc import Callable, Sequence
from typing import Any, Protocol, TypeAlias, TypeVar

from ftrs_common.feature_flags.feature_flag_config import FeatureFlag
from ftrs_common.feature_flags.feature_flags_client import is_enabled
from ftrs_common.logger import LogBase, Logger

ArgumentT = TypeVar("ArgumentT")
ResourceT = TypeVar("ResourceT")
ResponseT = TypeVar("ResponseT")
RequestGuardResult: TypeAlias = Any | None


class RequestGuard(Protocol):
    def __call__(self, arg: Any) -> RequestGuardResult: ...


class RequestGuardChain:
    def __init__(
        self,
        guards: Sequence[Callable[[Any], Any | None]],
        handler: Callable[[Any], Any],
    ) -> None:
        self._guards = tuple(guards)
        self._handler = handler

    def handle(self, arg: Any) -> Any:
        for guard in self._guards:
            response = guard(arg)
            if response is not None:
                return response
        return self._handler(arg)


def _resolve_flag_config_name(flag_name: FeatureFlag | str) -> str:
    return flag_name.value if isinstance(flag_name, FeatureFlag) else flag_name


def _resolve_flag_log_name(flag_name: FeatureFlag | str) -> str:
    return flag_name.name if isinstance(flag_name, FeatureFlag) else flag_name


def build_enabled_feature_flag_handler(
    *,
    flag_name: FeatureFlag | str,
    logger: Logger,
    log_reference: LogBase,
    handler: Callable[[ArgumentT], ResponseT],
    log_context: dict[str, Any] | None = None,
) -> Callable[[ArgumentT], ResponseT]:
    resolved_flag_name = _resolve_flag_log_name(flag_name)
    extra_context = log_context or {}

    def _enabled_handler(arg: ArgumentT) -> ResponseT:
        logger.log(
            log_reference,
            feature_flag=resolved_flag_name,
            feature_flag_status="enabled",
            **extra_context,
        )
        return handler(arg)

    return _enabled_handler


def build_disabled_feature_flag_handler(
    *,
    flag_name: FeatureFlag | str,
    logger: Logger,
    log_reference: LogBase,
    create_error_resource: Callable[[], ResourceT],
    get_response_size_and_duration: Callable[[ResourceT, float, Logger], tuple[int, int]],
    create_response: Callable[[int, ResourceT], ResponseT],
    status_code: int = 503,
    log_context: dict[str, Any] | None = None,
) -> Callable[[float], ResponseT]:
    resolved_flag_name = _resolve_flag_log_name(flag_name)
    extra_context = log_context or {}

    def _disabled_handler(start: float) -> ResponseT:
        error_resource = create_error_resource()
        response_size, duration_ms = get_response_size_and_duration(
            error_resource, start, logger
        )
        logger.log(
            log_reference,
            feature_flag=resolved_flag_name,
            feature_flag_status="disabled",
            dos_response_time=f"{duration_ms}ms",
            dos_response_size=response_size,
            **extra_context,
        )
        return create_response(status_code, error_resource)

    return _disabled_handler


def build_feature_flag_guard(
    *,
    flag_name: FeatureFlag | str,
    logger_getter: Callable[[], Logger],
    enabled_log_reference: LogBase,
    disabled_log_reference: LogBase,
    create_error_resource_getter: Callable[[], Callable[[], ResourceT]],
    get_response_size_and_duration_getter: Callable[
        [], Callable[[ResourceT, float, Logger], tuple[int, int]]
    ],
    create_response_getter: Callable[[], Callable[[int, ResourceT], ResponseT]],
    log_context: dict[str, Any] | None = None,
    status_code: int = 503,
    default: bool = False,
) -> Callable[[float], ResponseT | None]:
    resolved_flag_log_name = _resolve_flag_log_name(flag_name)
    resolved_flag_config_name = _resolve_flag_config_name(flag_name)
    extra_context = log_context or {}

    def _guard(start: float) -> ResponseT | None:
        if is_enabled(resolved_flag_config_name, default):
            logger_getter().log(
                enabled_log_reference,
                feature_flag=resolved_flag_log_name,
                feature_flag_status="enabled",
                **extra_context,
            )
            return None

        return build_disabled_feature_flag_handler(
            flag_name=flag_name,
            logger=logger_getter(),
            log_reference=disabled_log_reference,
            create_error_resource=create_error_resource_getter(),
            get_response_size_and_duration=get_response_size_and_duration_getter(),
            create_response=create_response_getter(),
            status_code=status_code,
            log_context=log_context,
        )(start)

    return _guard


def build_feature_flag_guard_chain(
    *,
    flag_name: FeatureFlag | str,
    logger_getter: Callable[[], Logger],
    enabled_log_reference: LogBase,
    disabled_log_reference: LogBase,
    create_error_resource_getter: Callable[[], Callable[[], ResourceT]],
    get_response_size_and_duration_getter: Callable[
        [], Callable[[ResourceT, float, Logger], tuple[int, int]]
    ],
    create_response_getter: Callable[[], Callable[[int, ResourceT], ResponseT]],
    handler: Callable[[float], ResponseT],
    additional_guards: Sequence[Callable[[float], ResponseT | None]] = (),
    log_context: dict[str, Any] | None = None,
    status_code: int = 503,
    default: bool = False,
) -> RequestGuardChain:
    feature_flag_guard = build_feature_flag_guard(
        flag_name=flag_name,
        logger_getter=logger_getter,
        enabled_log_reference=enabled_log_reference,
        disabled_log_reference=disabled_log_reference,
        create_error_resource_getter=create_error_resource_getter,
        get_response_size_and_duration_getter=get_response_size_and_duration_getter,
        create_response_getter=create_response_getter,
        log_context=log_context,
        status_code=status_code,
        default=default,
    )
    return RequestGuardChain(
        guards=[feature_flag_guard, *additional_guards],
        handler=handler,
    )


__all__ = [
    "RequestGuard",
    "RequestGuardChain",
    "build_disabled_feature_flag_handler",
    "build_enabled_feature_flag_handler",
    "build_feature_flag_guard",
    "build_feature_flag_guard_chain",
    "_resolve_flag_config_name",
]

