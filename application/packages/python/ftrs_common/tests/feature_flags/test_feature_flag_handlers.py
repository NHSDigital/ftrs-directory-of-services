from unittest.mock import MagicMock, patch

from ftrs_common.feature_flags import (
    FeatureFlag,
    RequestGuardChain,
    build_disabled_feature_flag_handler,
    build_enabled_feature_flag_handler,
    build_feature_flag_guard,
    build_feature_flag_guard_chain,
)
from ftrs_common.logbase import FeatureFlagLogBase


def test_build_enabled_feature_flag_handler_logs_and_calls_handler() -> None:
    logger = MagicMock()
    wrapped_handler = MagicMock(return_value="enabled-result")
    handler = build_enabled_feature_flag_handler(
        flag_name=FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED,
        logger=logger,
        log_reference=FeatureFlagLogBase.FF_002,
        handler=wrapped_handler,
        log_context={"dos_message_category": "FEATURE_FLAG"},
    )

    result = handler(12.0)

    assert result == "enabled-result"
    logger.log.assert_called_once_with(
        FeatureFlagLogBase.FF_002,
        feature_flag="DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED",
        feature_flag_status="enabled",
        dos_message_category="FEATURE_FLAG",
    )
    wrapped_handler.assert_called_once_with(12.0)


def test_build_disabled_feature_flag_handler_logs_and_builds_response() -> None:
    logger = MagicMock()
    create_error_resource = MagicMock(return_value="error-resource")
    get_response_size_and_duration = MagicMock(return_value=(68, 3))
    create_response = MagicMock(return_value="disabled-response")
    handler = build_disabled_feature_flag_handler(
        flag_name=FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED,
        logger=logger,
        log_reference=FeatureFlagLogBase.FF_002,
        create_error_resource=create_error_resource,
        get_response_size_and_duration=get_response_size_and_duration,
        create_response=create_response,
        log_context={"dos_message_category": "FEATURE_FLAG"},
    )

    result = handler(12.0)

    assert result == "disabled-response"
    create_error_resource.assert_called_once_with()
    get_response_size_and_duration.assert_called_once_with(
        "error-resource", 12.0, logger
    )
    logger.log.assert_called_once_with(
        FeatureFlagLogBase.FF_002,
        feature_flag="DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED",
        feature_flag_status="disabled",
        dos_response_time="3ms",
        dos_response_size=68,
        dos_message_category="FEATURE_FLAG",
    )
    create_response.assert_called_once_with(503, "error-resource")


def test_build_feature_flag_guard_allows_request_when_enabled() -> None:
    logger = MagicMock()
    create_error_resource_getter = MagicMock()
    create_response_getter = MagicMock()

    with patch(
        "ftrs_common.feature_flags.feature_flag_handlers.is_enabled"
    ) as mock_is_enabled:
        mock_is_enabled.return_value = True

        guard = build_feature_flag_guard(
            flag_name=FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED,
            logger_getter=lambda: logger,
            enabled_log_reference=FeatureFlagLogBase.FF_002,
            disabled_log_reference=FeatureFlagLogBase.FF_005,
            create_error_resource_getter=create_error_resource_getter,
            get_response_size_and_duration_getter=MagicMock(),
            create_response_getter=create_response_getter,
            log_context={"dos_message_category": "FEATURE_FLAG"},
        )

        result = guard(12.0)

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
            flag_name=FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED,
            logger_getter=lambda: logger,
            enabled_log_reference=FeatureFlagLogBase.FF_002,
            disabled_log_reference=FeatureFlagLogBase.FF_005,
            create_error_resource_getter=lambda: create_error_resource,
            get_response_size_and_duration_getter=(
                lambda: get_response_size_and_duration
            ),
            create_response_getter=lambda: create_response,
            log_context={"dos_message_category": "FEATURE_FLAG"},
        )

        result = guard(12.0)

    assert result == "disabled-response"
    mock_is_enabled.assert_called_once_with(
        FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED.value,
        False,
    )
    create_error_resource.assert_called_once_with()
    get_response_size_and_duration.assert_called_once_with(
        "error-resource", 12.0, logger
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
    first_guard = MagicMock(return_value=None)
    second_guard = MagicMock(return_value=None)
    handler = MagicMock(return_value="handled")
    chain = RequestGuardChain([first_guard, second_guard], handler)

    result = chain.handle(7.0)

    assert result == "handled"
    first_guard.assert_called_once_with(7.0)
    second_guard.assert_called_once_with(7.0)
    handler.assert_called_once_with(7.0)


def test_request_guard_chain_stops_on_first_guard_response() -> None:
    first_guard = MagicMock(return_value="blocked")
    second_guard = MagicMock(return_value=None)
    handler = MagicMock(return_value="handled")
    chain = RequestGuardChain([first_guard, second_guard], handler)

    result = chain.handle(7.0)

    assert result == "blocked"
    first_guard.assert_called_once_with(7.0)
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
            flag_name="dos_search_healthcare_service_enabled",
            logger_getter=logger_getter,
            enabled_log_reference=FeatureFlagLogBase.FF_002,
            disabled_log_reference=FeatureFlagLogBase.FF_005,
            create_error_resource_getter=create_error_resource_getter,
            get_response_size_and_duration_getter=get_response_size_and_duration_getter,
            create_response_getter=create_response_getter,
            handler=handler,
            log_context={"dos_message_category": "FEATURE_FLAG"},
        )

    assert isinstance(chain, RequestGuardChain)
    mock_build_guard.assert_called_once_with(
        flag_name="dos_search_healthcare_service_enabled",
        logger_getter=logger_getter,
        enabled_log_reference=FeatureFlagLogBase.FF_002,
        disabled_log_reference=FeatureFlagLogBase.FF_005,
        create_error_resource_getter=create_error_resource_getter,
        get_response_size_and_duration_getter=get_response_size_and_duration_getter,
        create_response_getter=create_response_getter,
        log_context={"dos_message_category": "FEATURE_FLAG"},
        status_code=503,
        default=False,
    )

    result = chain.handle(7.0)

    assert result == "handled"
    guard.assert_called_once_with(7.0)
    handler.assert_called_once_with(7.0)

