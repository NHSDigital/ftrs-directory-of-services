from pathlib import Path
from typing import Literal

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from pipeline.extract import (
    extract,
    extract_gp_practice,
    format_endpoints,
    main,
    merge_gp_practice_with_endpoints,
)

mock_gp_practices_df = pd.DataFrame(
    {
        "name": ["Practice A"],
        "type": ["GP"],
        "odscode": ["A12345"],
        "uid": ["uid123"],
        "serviceid": [1],
    }
)

mock_gp_endpoints_df = pd.DataFrame(
    {
        "id": [1],
        "endpointorder": [1],
        "transport": ["email"],
        "format": ["PDF"],
        "interaction": ["interaction1"],
        "businessscenario": ["scenario1"],
        "address": ["address1"],
        "comment": ["comment1"],
        "iscompressionenabled": ["false"],
        "serviceid": [1],
    }
)

mock_gp_endpoints_formatted_df = pd.DataFrame(
    {
        "serviceid": [1],
        "endpoints": [
            [
                {
                    "endpointid": 1,
                    "endpointorder": 1,
                    "transport": "email",
                    "format": "PDF",
                    "interaction": "interaction1",
                    "businessscenario": "scenario1",
                    "address": "address1",
                    "comment": "comment1",
                    "iscompressionenabled": "false",
                    "serviceid": 1,
                }
            ]
        ],
    }
)


mock_gp_practice_extract_df = pd.DataFrame(
    {
        "name": ["Practice A"],
        "type": ["GP"],
        "odscode": ["A12345"],
        "uid": ["uid123"],
        "endpoints": [
            [
                {
                    "endpointid": 1,
                    "endpointorder": 1,
                    "transport": "email",
                    "format": "PDF",
                    "interaction": "interaction1",
                    "businessscenario": "scenario1",
                    "address": "address1",
                    "comment": "comment1",
                    "iscompressionenabled": "false",
                    "serviceid": 1,
                }
            ]
        ],
    }
)


def test_extract(mocker: MockerFixture) -> None:
    """
    Test that extract logs the output path and calls extract_gp_practice
    """
    mock_logging_info = mocker.patch("pipeline.extract.logging.info")
    mock_extract_gp_practice = mocker.patch("pipeline.extract.extract_gp_practice")

    extract("test_db_uri", Path("test_output_path"))

    mock_logging_info.assert_called_once_with("Extracting data to test_output_path")
    # TODO: use something like freezegun to freeze time to mock the timestamp - instead of mocker.ANY ?
    mock_extract_gp_practice.assert_called_once_with(
        "test_db_uri", Path("test_output_path"), mocker.ANY
    )


def test_main_parses_args(mocker: MockerFixture) -> None:
    """
    Test that main parses command line arguments and calls extract with the correct arguments
    """
    extract_mock = mocker.patch("pipeline.extract.extract")
    args = ["--db-uri", "test_db_uri", "--output-path", "test_output_path"]

    main(args)

    assert extract_mock.called is True
    assert extract_mock.call_args[0][0] == "test_db_uri"
    assert extract_mock.call_args[0][1] == Path("test_output_path")


@pytest.mark.parametrize(
    "args, expected_exit_code",
    [
        ([""], 2),
        (["--output-path", "test_output_path"], 2),
    ],
)
def test_main_throws_error_on_invalid_args(
    mocker: MockerFixture, args: list[str], expected_exit_code: Literal[2]
) -> None:
    """
    Test that main throws an error when no arguments are provided
    Test that main throws an error when required arguments are missing
    """
    extract_mock = mocker.patch("pipeline.extract.extract")

    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert extract_mock.called is False


def test_extract_gp_practice(mocker: MockerFixture) -> None:
    """
    Test the extract_gp_practice function calls its dependencies with the correct arguments,
    and logs the expected messages.
    """
    mock_get_gp_practices = mocker.patch(
        "pipeline.extract.get_gp_practices", return_value=mock_gp_practices_df
    )
    mock_get_gp_endpoints = mocker.patch(
        "pipeline.extract.get_gp_endpoints", return_value=mock_gp_endpoints_df
    )
    mock_get_services_size = mocker.patch(
        "pipeline.extract.get_services_size", return_value=1
    )
    mock_get_services_columns = mocker.patch(
        "pipeline.extract.get_services_columns_count", return_value=37
    )
    mock_get_serviceendpoints_columns = mocker.patch(
        "pipeline.extract.get_serviceendpoints_columns_count", return_value=10
    )
    mock_to_parquet = mocker.patch("pandas.DataFrame.to_parquet")
    mock_logging_info = mocker.patch("pipeline.extract.logging.info")

    extract_gp_practice("test_db_uri", Path("test_output_path"), "20250310144346")

    mock_get_gp_practices.assert_called_once_with("test_db_uri")
    mock_get_gp_endpoints.assert_called_once_with("test_db_uri")
    mock_get_services_size.assert_called_once_with("test_db_uri")
    mock_get_services_columns.assert_called_once_with("test_db_uri")
    mock_get_serviceendpoints_columns.assert_called_once_with("test_db_uri")
    mock_to_parquet.assert_called_once_with(
        Path("test_output_path") / "dos-gp-practice-extract-20250310144346.parquet",
        engine="pyarrow",
        index=False,
        compression="zstd",
    )
    mock_logging_info.assert_any_call("Percentage of service profiles: 100.0%")
    mock_logging_info.assert_any_call("Percentage of all data fields: 10.64%")


@pytest.mark.parametrize(
    "input_df, expected_df",
    [
        (
            pd.DataFrame(
                {
                    "id": [1, 2],
                    "endpointorder": [1, 2],
                    "transport": ["email", "sms"],
                    "format": ["PDF", "XML"],
                    "interaction": ["interaction1", "interaction2"],
                    "businessscenario": ["scenario1", "scenario2"],
                    "address": ["address1", "address2"],
                    "comment": ["comment1", "comment2"],
                    "iscompressionenabled": ["false", "true"],
                    "serviceid": [1, 1],
                }
            ),
            pd.DataFrame(
                {
                    "serviceid": [1],
                    "endpoints": [
                        [
                            {
                                "endpointid": 1,
                                "endpointorder": 1,
                                "transport": "email",
                                "format": "PDF",
                                "interaction": "interaction1",
                                "businessscenario": "scenario1",
                                "address": "address1",
                                "comment": "comment1",
                                "iscompressionenabled": "false",
                                "serviceid": 1,
                            },
                            {
                                "endpointid": 2,
                                "endpointorder": 2,
                                "transport": "sms",
                                "format": "XML",
                                "interaction": "interaction2",
                                "businessscenario": "scenario2",
                                "address": "address2",
                                "comment": "comment2",
                                "iscompressionenabled": "true",
                                "serviceid": 1,
                            },
                        ]
                    ],
                }
            ),
        ),
        (
            pd.DataFrame(
                {
                    "id": [1, 2, 3],
                    "endpointorder": [1, 1, 2],
                    "transport": ["email", "sms", "fax"],
                    "format": ["PDF", "XML", "TXT"],
                    "interaction": ["interaction1", "interaction2", "interaction3"],
                    "businessscenario": ["scenario1", "scenario2", "scenario3"],
                    "address": ["address1", "address2", "address3"],
                    "comment": ["comment1", "comment2", "comment3"],
                    "iscompressionenabled": ["false", "true", "false"],
                    "serviceid": [1, 2, 2],
                }
            ),
            pd.DataFrame(
                {
                    "serviceid": [1, 2],
                    "endpoints": [
                        [
                            {
                                "endpointid": 1,
                                "endpointorder": 1,
                                "transport": "email",
                                "format": "PDF",
                                "interaction": "interaction1",
                                "businessscenario": "scenario1",
                                "address": "address1",
                                "comment": "comment1",
                                "iscompressionenabled": "false",
                                "serviceid": 1,
                            }
                        ],
                        [
                            {
                                "endpointid": 2,
                                "endpointorder": 1,
                                "transport": "sms",
                                "format": "XML",
                                "interaction": "interaction2",
                                "businessscenario": "scenario2",
                                "address": "address2",
                                "comment": "comment2",
                                "iscompressionenabled": "true",
                                "serviceid": 2,
                            },
                            {
                                "endpointid": 3,
                                "endpointorder": 2,
                                "transport": "fax",
                                "format": "TXT",
                                "interaction": "interaction3",
                                "businessscenario": "scenario3",
                                "address": "address3",
                                "comment": "comment3",
                                "iscompressionenabled": "false",
                                "serviceid": 2,
                            },
                        ],
                    ],
                }
            ),
        ),
    ],
)
def test_format_endpoints(input_df: pd.DataFrame, expected_df: pd.DataFrame) -> None:
    """
    Test the format_endpoints function with one service ID
    Test the format_endpoints function with different service IDs
    """
    result = format_endpoints(input_df)
    pd.testing.assert_frame_equal(result, expected_df)


@pytest.mark.parametrize(
    "gp_practice_df, grouped_endpoints, expected_df",
    [
        (
            mock_gp_practices_df,
            mock_gp_endpoints_formatted_df,
            mock_gp_practice_extract_df,
        ),
        (
            pd.DataFrame(
                {
                    "name": ["Practice A", "Practice B"],
                    "type": ["GP", "GP"],
                    "odscode": ["A12345", "B67890"],
                    "uid": ["uid123", "uid456"],
                    "serviceid": [1, 2],
                }
            ),
            pd.DataFrame(
                {
                    "serviceid": [1, 2],
                    "endpoints": [
                        [
                            {
                                "endpointid": 1,
                                "endpointorder": 1,
                                "transport": "email",
                                "format": "PDF",
                                "interaction": "interaction1",
                                "businessscenario": "scenario1",
                                "address": "address1",
                                "comment": "comment1",
                                "iscompressionenabled": "false",
                                "serviceid": 1,
                            }
                        ],
                        [
                            {
                                "endpointid": 2,
                                "endpointorder": 1,
                                "transport": "sms",
                                "format": "XML",
                                "interaction": "interaction2",
                                "businessscenario": "scenario2",
                                "address": "address2",
                                "comment": "comment2",
                                "iscompressionenabled": "true",
                                "serviceid": 2,
                            }
                        ],
                    ],
                }
            ),
            pd.DataFrame(
                {
                    "name": ["Practice A", "Practice B"],
                    "type": ["GP", "GP"],
                    "odscode": ["A12345", "B67890"],
                    "uid": ["uid123", "uid456"],
                    "endpoints": [
                        [
                            {
                                "endpointid": 1,
                                "endpointorder": 1,
                                "transport": "email",
                                "format": "PDF",
                                "interaction": "interaction1",
                                "businessscenario": "scenario1",
                                "address": "address1",
                                "comment": "comment1",
                                "iscompressionenabled": "false",
                                "serviceid": 1,
                            }
                        ],
                        [
                            {
                                "endpointid": 2,
                                "endpointorder": 1,
                                "transport": "sms",
                                "format": "XML",
                                "interaction": "interaction2",
                                "businessscenario": "scenario2",
                                "address": "address2",
                                "comment": "comment2",
                                "iscompressionenabled": "true",
                                "serviceid": 2,
                            }
                        ],
                    ],
                }
            ),
        ),
        (
            pd.DataFrame(
                {
                    "name": ["Practice A"],
                    "type": ["GP"],
                    "odscode": ["A12345"],
                    "uid": ["uid123"],
                    "serviceid": [1],
                }
            ),
            pd.DataFrame(
                {
                    "serviceid": [2],
                    "endpoints": [
                        [
                            {
                                "endpointid": 2,
                                "endpointorder": 1,
                                "transport": "sms",
                                "format": "XML",
                                "interaction": "interaction2",
                                "businessscenario": "scenario2",
                                "address": "address2",
                                "comment": "comment2",
                                "iscompressionenabled": "true",
                                "serviceid": 2,
                            }
                        ]
                    ],
                }
            ),
            pd.DataFrame(
                {
                    "name": ["Practice A"],
                    "type": ["GP"],
                    "odscode": ["A12345"],
                    "uid": ["uid123"],
                    "endpoints": None,
                }
            ),
        ),
    ],
)
def test_merge_gp_practice_with_endpoints(
    gp_practice_df: pd.DataFrame,
    grouped_endpoints: pd.DataFrame,
    expected_df: pd.DataFrame,
) -> None:
    """
    Test the merge_gp_practice_with_endpoints function
    Test the merge_gp_practice_with_endpoints function with multiple service IDs
    Test the merge_gp_practice_with_endpoints function with mismatched service IDs
    """
    result = merge_gp_practice_with_endpoints(gp_practice_df, grouped_endpoints)
    # assertion for the third test scenario of mismatched service IDs
    if "endpoints" in expected_df.columns and expected_df["endpoints"].iloc[0] is None:
        assert pd.isna(result["endpoints"].iloc[0])
        columns_to_compare = ["name", "type", "odscode", "uid"]
        for column in columns_to_compare:
            assert result[column].iloc[0] == expected_df[column].iloc[0]

    else:
        pd.testing.assert_frame_equal(result, expected_df)
