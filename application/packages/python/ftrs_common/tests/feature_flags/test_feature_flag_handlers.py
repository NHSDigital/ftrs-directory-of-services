from unittest.mock import MagicMock, patch

from ftrs_common.feature_flags import (
    FeatureFlag,
    FeatureFlagGuardConfig,
    FeatureFlagGuardDependencies,
    RequestGuard,
    RequestGuardChain,
    build_feature_flag_guard,
    build_feature_flag_guard_chain,
)
from ftrs_common.logbase import FeatureFlagLogBase

type FloatStringRequestGuard = RequestGuard[float, str]
REQUEST_START_TIME = 12.0


def test_build_feature_flag_guard_allows_request_when_enabled() -> None:
    logger = MagicMock()
    create_error_resource_getter = MagicMock()
    create_response_getter = MagicMock()

    with patch(
        "ftrs_common.feature_flags.feature_flag_handlers.is_enabled"
    ) as mock_is_enabled:
        mock_is_enabled.return_value = True

        guard = build_feature_flag_guard(
            config=FeatureFlagGuardConfig(
                flag_name=FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED,
                enabled_log_reference=FeatureFlagLogBase.FF_002,
                disabled_log_reference=FeatureFlagLogBase.FF_005,
                log_context={"dos_message_category": "FEATURE_FLAG"},
            ),
            dependencies=FeatureFlagGuardDependencies(
                logger_getter=lambda: logger,
                create_error_resource_getter=create_error_resource_getter,
                get_response_size_and_duration_getter=MagicMock(),
                create_response_getter=create_response_getter,
            ),
        )

        result = guard(REQUEST_START_TIME)

    assert result is None
    mock_is_enabled.assert_called_once_with(
        FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED.value,
        False,
    )
    logger.log.assert_called_once_with(
        FeatureFlagLogBase.FF_002,
        feature_flag="DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED",
        feature_flag_status="enabled",
        dos_message_category="FEATURE_FLAG",
    )
    create_error_resource_getter.assert_not_called()
    create_response_getter.assert_not_called()


def test_build_feature_flag_guard_short_circuits_when_disabled() -> None:
    logger = MagicMock()
    create_error_resource = MagicMock(return_value="error-resource")
    get_response_size_and_duration = MagicMock(return_value=(68, 3))
    create_response = MagicMock(return_value="disabled-response")

    with patch(
        "ftrs_common.feature_flags.feature_flag_handlers.is_enabled"
    ) as mock_is_enabled:
        mock_is_enabled.return_value = False

        guard = build_feature_flag_guard(
            config=FeatureFlagGuardConfig(
                flag_name=FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED,
                enabled_log_reference=FeatureFlagLogBase.FF_002,
                disabled_log_reference=FeatureFlagLogBase.FF_005,
                log_context={"dos_message_category": "FEATURE_FLAG"},
            ),
            dependencies=FeatureFlagGuardDependencies(
                logger_getter=lambda: logger,
                create_error_resource_getter=lambda: create_error_resource,
                get_response_size_and_duration_getter=(
                    lambda: get_response_size_and_duration
                ),
                create_response_getter=lambda: create_response,
            ),
        )

        result = guard(REQUEST_START_TIME)

    assert result == "disabled-response"
    mock_is_enabled.assert_called_once_with(
        FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED.value,
        False,
    )
    create_error_resource.assert_called_once_with()
    get_response_size_and_duration.assert_called_once_with(
        "error-resource", REQUEST_START_TIME, logger
    )
    logger.log.assert_called_once_with(
        FeatureFlagLogBase.FF_005,
        feature_flag="DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED",
        feature_flag_status="disabled",
        dos_response_time="3ms",
        dos_response_size=68,
        dos_message_category="FEATURE_FLAG",
    )
    create_response.assert_called_once_with(503, "error-resource")


def test_request_guard_chain_runs_next_handler_when_guards_pass() -> None:
    first_guard: FloatStringRequestGuard = MagicMock(return_value=None)
    second_guard: FloatStringRequestGuard = MagicMock(return_value=None)
    handler = MagicMock(return_value="handled")
    chain = RequestGuardChain([first_guard, second_guard], handler)

    result = chain.handle(REQUEST_START_TIME)

    assert result == "handled"
    first_guard.assert_called_once_with(REQUEST_START_TIME)
    second_guard.assert_called_once_with(REQUEST_START_TIME)
    handler.assert_called_once_with(REQUEST_START_TIME)


def test_request_guard_chain_stops_on_first_guard_response() -> None:
    first_guard: FloatStringRequestGuard = MagicMock(return_value="blocked")
    second_guard: FloatStringRequestGuard = MagicMock(return_value=None)
    handler = MagicMock(return_value="handled")
    chain = RequestGuardChain([first_guard, second_guard], handler)

    result = chain.handle(REQUEST_START_TIME)

    assert result == "blocked"
    first_guard.assert_called_once_with(REQUEST_START_TIME)
    second_guard.assert_not_called()
    handler.assert_not_called()


def test_build_feature_flag_guard_chain_wraps_handler_with_feature_flag_guard() -> None:
    handler = MagicMock(return_value="handled")
    logger_getter = MagicMock()
    create_error_resource_getter = MagicMock()
    get_response_size_and_duration_getter = MagicMock()
    create_response_getter = MagicMock()

    with patch(
        "ftrs_common.feature_flags.feature_flag_handlers.build_feature_flag_guard"
    ) as mock_build_guard:
        guard = MagicMock(return_value=None)
        mock_build_guard.return_value = guard

        chain = build_feature_flag_guard_chain(
            config=FeatureFlagGuardConfig(
                flag_name="dos_search_healthcare_service_enabled",
                enabled_log_reference=FeatureFlagLogBase.FF_002,
                disabled_log_reference=FeatureFlagLogBase.FF_005,
                log_context={"dos_message_category": "FEATURE_FLAG"},
            ),
            dependencies=FeatureFlagGuardDependencies(
                logger_getter=logger_getter,
                create_error_resource_getter=create_error_resource_getter,
                get_response_size_and_duration_getter=(
                    get_response_size_and_duration_getter
                ),
                create_response_getter=create_response_getter,
            ),
            handler=handler,
        )

    assert isinstance(chain, RequestGuardChain)
    mock_build_guard.assert_called_once_with(
        config=FeatureFlagGuardConfig(
            flag_name="dos_search_healthcare_service_enabled",
            enabled_log_reference=FeatureFlagLogBase.FF_002,
            disabled_log_reference=FeatureFlagLogBase.FF_005,
            log_context={"dos_message_category": "FEATURE_FLAG"},
        ),
        dependencies=FeatureFlagGuardDependencies(
            logger_getter=logger_getter,
            create_error_resource_getter=create_error_resource_getter,
            get_response_size_and_duration_getter=get_response_size_and_duration_getter,
            create_response_getter=create_response_getter,
        ),
    )

    result = chain.handle(REQUEST_START_TIME)

    assert result == "handled"
    guard.assert_called_once_with(REQUEST_START_TIME)
    handler.assert_called_once_with(REQUEST_START_TIME)
