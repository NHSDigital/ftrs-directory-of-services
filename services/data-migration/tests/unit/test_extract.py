from io import BytesIO
from pathlib import Path
from typing import Literal

import pandas as pd
import pyarrow.parquet as pq
import pytest
from pytest_mock import MockerFixture

from pipeline.exceptions import ExtractArgsError
from pipeline.extract import (
    convert_to_parquet_buffer,
    extract,
    extract_gp_practice,
    format_endpoints,
    main,
    merge_gp_practice_with_endpoints,
    store_local,
    store_s3,
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


@pytest.mark.parametrize(
    "db_uri, output_path, s3_output_uri, expected_log",
    [
        (
            "test_db_uri",
            Path("test_output_path"),
            None,
            "Extracting data to test_output_path",
        ),
        (
            "test_db_uri",
            None,
            "s3://test_s3_output_uri",
            "Extracting data to s3://test_s3_output_uri",
        ),
    ],
)
def test_extract(
    mocker: MockerFixture,
    db_uri: str,
    output_path: Path,
    s3_output_uri: str,
    expected_log: str,
) -> None:
    """
    Test that extract logs the output path and calls extract_gp_practice
    """
    mock_logging_info = mocker.patch("pipeline.extract.logging.info")
    mock_extract_gp_practice = mocker.patch("pipeline.extract.extract_gp_practice")
    mock_store_local = mocker.patch("pipeline.extract.store_local")
    mock_store_s3 = mocker.patch("pipeline.extract.store_s3")

    extract(db_uri, output_path, s3_output_uri)

    if output_path:
        mock_store_local.assert_called()
        mock_store_s3.assert_not_called()
    if s3_output_uri:
        mock_store_s3.assert_called()
        mock_store_local.assert_not_called()

    mock_logging_info.assert_called_once_with(expected_log)
    mock_extract_gp_practice.assert_called_once_with(db_uri)


@pytest.mark.parametrize(
    "args, expected_db_uri, expected_output_path, expected_s3_output_uri",
    [
        # valid output path args
        (
            ["--db-uri", "test_db_uri", "--output-path", "test_output_path"],
            "test_db_uri",
            Path("test_output_path"),
            None,
        ),
        # valid S3 output URI args
        (
            ["--db-uri", "test_db_uri", "--s3-output-uri", "s3://bucket/path"],
            "test_db_uri",
            None,
            "s3://bucket/path",
        ),
    ],
)
def test_main_parses_args(
    mocker: MockerFixture,
    args: list[str],
    expected_db_uri: str,
    expected_output_path: Path,
    expected_s3_output_uri: str,
) -> None:
    """
    Test that main parses command line arguments and calls extract with the correct arguments.
    """

    extract_mock = mocker.patch("pipeline.extract.extract")

    if "--s3-output-uri" in args:
        mock_validate_s3_uri = mocker.patch("pipeline.extract.validate_s3_uri")
        mock_validate_s3_uri.return_value = expected_s3_output_uri

    main(args)

    assert extract_mock.called is True
    assert extract_mock.call_args[0][0] == expected_db_uri
    assert extract_mock.call_args[0][1] == expected_output_path
    assert extract_mock.call_args[0][2] == expected_s3_output_uri


@pytest.mark.parametrize(
    "args, expected_exit_code",
    [
        ([""], 2),
        (["--output-path", "test_output_path"], 2),
        (["--s3-output-uri", "s3://bucket/path"], 2),
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
    mocker.patch("pipeline.extract.validate_s3_uri")

    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert extract_mock.called is False


@pytest.mark.parametrize(
    "args",
    [
        [
            "--db-uri",
            "test_db_uri",
            "--output-path",
            "test_output_path",
            "--s3-output-uri",
            "s3://bucket/path",
        ],
        ["--db-uri", "test_db_uri"],
    ],
)
def test_main_raises_extractargserror(mocker: MockerFixture, args: list[str]) -> None:
    """
    Test that main raises ExtractArgsError when invalid argument combinations are provided.
    """
    mocker.patch("pipeline.extract.extract")

    if "--s3-output-uri" in args:
        mock_validate_s3_uri = mocker.patch("pipeline.extract.validate_s3_uri")
        mock_validate_s3_uri.return_value = "s3://bucket/path"

    with pytest.raises(ExtractArgsError):
        main(args)


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
    mock_logging_info = mocker.patch("pipeline.extract.logging.info")

    extract_gp_practice("test_db_uri")

    mock_get_gp_practices.assert_called_once_with("test_db_uri")
    mock_get_gp_endpoints.assert_called_once_with("test_db_uri")
    mock_get_services_size.assert_called_once_with("test_db_uri")
    mock_get_services_columns.assert_called_once_with("test_db_uri")
    mock_get_serviceendpoints_columns.assert_called_once_with("test_db_uri")
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


def test_store_local(mocker: MockerFixture) -> None:
    mock_to_parquet = mocker.patch("pandas.DataFrame.to_parquet")
    mock_path = mocker.MagicMock(spec=Path)
    mock_path.__truediv__.return_value = mock_path / "test.parquet"

    # TODO: use something like freezegun to freeze time to mock the timestamp - instead of mocker.ANY ?
    store_local(mock_gp_practice_extract_df, mock_path, "20230402", "test_extract")

    mock_to_parquet.assert_called_once_with(
        mock_path / "test_extract-20230402.parquet",
        engine="pyarrow",
        index=False,
        compression="zstd",
    )


def test_convert_to_parquet_buffer() -> None:
    """
    Test that convert_to_parquet_buffer converts a DataFrame to a Parquet buffer.
    """
    buffer = convert_to_parquet_buffer(mock_gp_practice_extract_df)

    assert isinstance(buffer, BytesIO), "The result should be a BytesIO object."
    buffer.seek(0)  # Reset buffer position to the beginning
    table = pq.read_table(buffer)
    result_df = table.to_pandas()
    pd.testing.assert_frame_equal(result_df, mock_gp_practice_extract_df)


def test_store_s3(mocker: MockerFixture) -> None:
    mock_convert_to_parquet_buffer = mocker.patch(
        "pipeline.extract.convert_to_parquet_buffer"
    )
    mock_bucket_wrapper = mocker.patch("pipeline.extract.BucketWrapper")
    mock_buffer = BytesIO(b"test data")
    mock_convert_to_parquet_buffer.return_value = mock_buffer
    mock_instance = mock_bucket_wrapper.return_value
    mock_instance.s3_upload_file = mocker.patch(
        "pipeline.extract.BucketWrapper.s3_upload_file"
    )

    store_s3(mock_gp_practice_extract_df, "s3://your-bucket-name/path/to/object")

    mock_convert_to_parquet_buffer.assert_called_once_with(mock_gp_practice_extract_df)
    mock_instance.s3_upload_file.assert_called_once_with(
        mock_buffer, "dos-gp-practice-extract.parquet"
    )
