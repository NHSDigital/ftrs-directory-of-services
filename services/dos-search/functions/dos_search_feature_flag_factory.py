from collections.abc import Callable, Sequence

from aws_lambda_powertools.event_handler import Response
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.feature_flags import (
    FeatureFlag,
    RequestGuard,
    RequestGuardChain,
    build_feature_flag_guard,
    build_feature_flag_guard_chain,
)
from ftrs_common.logger import LogBase, Logger

from functions.event_context import get_response_size_and_duration


def build_dos_search_feature_flag_guard(
    *,
    flag_name: FeatureFlag | str,
    logger_getter: Callable[[], Logger],
    enabled_log_reference: LogBase,
    disabled_log_reference: LogBase,
    create_error_resource_getter: Callable[[], Callable[[], FHIRResourceModel]],
    create_response_getter: Callable[
        [], Callable[[int, FHIRResourceModel], Response]
    ],
    default: bool = False,
) -> RequestGuard:
    return build_feature_flag_guard(
        flag_name=flag_name,
        logger_getter=logger_getter,
        enabled_log_reference=enabled_log_reference,
        disabled_log_reference=disabled_log_reference,
        create_error_resource_getter=create_error_resource_getter,
        get_response_size_and_duration_getter=lambda: get_response_size_and_duration,
        create_response_getter=create_response_getter,
        log_context={"dos_message_category": "FEATURE_FLAG"},
        default=default,
    )


def build_dos_search_feature_flag_chain(
    *,
    flag_name: FeatureFlag | str,
    logger_getter: Callable[[], Logger],
    enabled_log_reference: LogBase,
    disabled_log_reference: LogBase,
    create_error_resource_getter: Callable[[], Callable[[], FHIRResourceModel]],
    create_response_getter: Callable[
        [], Callable[[int, FHIRResourceModel], Response]
    ],
    handler: Callable[[float], Response],
    additional_guards: Sequence[RequestGuard] = (),
    default: bool = False,
) -> RequestGuardChain:
    return build_feature_flag_guard_chain(
        flag_name=flag_name,
        logger_getter=logger_getter,
        enabled_log_reference=enabled_log_reference,
        disabled_log_reference=disabled_log_reference,
        create_error_resource_getter=create_error_resource_getter,
        get_response_size_and_duration_getter=lambda: get_response_size_and_duration,
        create_response_getter=create_response_getter,
        handler=handler,
        additional_guards=additional_guards,
        log_context={"dos_message_category": "FEATURE_FLAG"},
        default=default,
    )
