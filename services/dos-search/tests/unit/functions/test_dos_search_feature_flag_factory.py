from unittest.mock import ANY, MagicMock, patch

from functions.dos_search_feature_flag_factory import (
    build_dos_search_feature_flag_chain,
    build_dos_search_feature_flag_guard,
)
from functions.logbase import DosSearchLogBase


def test_build_dos_search_feature_flag_guard_uses_shared_builder_with_defaults() -> (
    None
):
    logger_getter = MagicMock()
    create_error_resource_getter = MagicMock()
    create_response_getter = MagicMock()

    with patch(
        "functions.dos_search_feature_flag_factory.build_feature_flag_guard"
    ) as mock_build_feature_flag_guard:
        mock_build_feature_flag_guard.return_value = MagicMock()

        result = build_dos_search_feature_flag_guard(
            flag_name="dos_search_healthcare_service_enabled",
            logger_getter=logger_getter,
            enabled_log_reference=DosSearchLogBase.DOS_SEARCH_014,
            disabled_log_reference=DosSearchLogBase.DOS_SEARCH_013,
            create_error_resource_getter=create_error_resource_getter,
            create_response_getter=create_response_getter,
        )

    assert result is mock_build_feature_flag_guard.return_value
    mock_build_feature_flag_guard.assert_called_once_with(
        flag_name="dos_search_healthcare_service_enabled",
        logger_getter=logger_getter,
        enabled_log_reference=DosSearchLogBase.DOS_SEARCH_014,
        disabled_log_reference=DosSearchLogBase.DOS_SEARCH_013,
        create_error_resource_getter=create_error_resource_getter,
        get_response_size_and_duration_getter=ANY,
        create_response_getter=create_response_getter,
        log_context={"dos_message_category": "FEATURE_FLAG"},
        default=False,
    )


def test_build_dos_search_feature_flag_chain_uses_shared_builder_with_defaults() -> (
    None
):
    logger_getter = MagicMock()
    create_error_resource_getter = MagicMock()
    create_response_getter = MagicMock()
    handler = MagicMock()
    additional_guards = [MagicMock()]

    with patch(
        "functions.dos_search_feature_flag_factory.build_feature_flag_guard_chain"
    ) as mock_build_feature_flag_chain:
        mock_build_feature_flag_chain.return_value = MagicMock()

        result = build_dos_search_feature_flag_chain(
            flag_name="dos_search_healthcare_service_enabled",
            logger_getter=logger_getter,
            enabled_log_reference=DosSearchLogBase.DOS_SEARCH_014,
            disabled_log_reference=DosSearchLogBase.DOS_SEARCH_013,
            create_error_resource_getter=create_error_resource_getter,
            create_response_getter=create_response_getter,
            handler=handler,
            additional_guards=additional_guards,
        )

    assert result is mock_build_feature_flag_chain.return_value
    mock_build_feature_flag_chain.assert_called_once_with(
        flag_name="dos_search_healthcare_service_enabled",
        logger_getter=logger_getter,
        enabled_log_reference=DosSearchLogBase.DOS_SEARCH_014,
        disabled_log_reference=DosSearchLogBase.DOS_SEARCH_013,
        create_error_resource_getter=create_error_resource_getter,
        get_response_size_and_duration_getter=ANY,
        create_response_getter=create_response_getter,
        handler=handler,
        additional_guards=additional_guards,
        log_context={"dos_message_category": "FEATURE_FLAG"},
        default=False,
    )
