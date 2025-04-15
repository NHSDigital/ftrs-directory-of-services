from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, call

import pandas as pd
import pyarrow.parquet as pq
import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from pipeline.db_utils import (
    QUERY_GP_ENDPOINTS,
    QUERY_GP_PRACTICE,
    QUERY_SERVICEENDPOINTS_COLUMNS,
    QUERY_SERVICES_COLUMNS,
    QUERY_SERVICES_SIZE,
)
from pipeline.extract import (
    convert_to_parquet_buffer,
    extract,
    extract_gp_practices,
    format_endpoints,
    merge_gp_practice_with_endpoints,
    store_local,
    store_s3,
)
from tests.util.stub_data import (
    mock_gp_endpoints_formatted_df,
    mock_gp_practice_extract_df,
    mock_gp_practices_df,
)


@pytest.mark.parametrize(
    "db_uri, output_path, s3_output_uri, expected_log",
    [
        (
            "test_db_uri",
            Path("test_output_path"),
            None,
            "Extracting data to test_output_path/2024-01-01T12-00-00",
        ),
        (
            "test_db_uri",
            None,
            "s3://test_s3_output_uri",
            "Extracting data to s3://test_s3_output_uri",
        ),
    ],
)
@freeze_time("2024-01-01 12:00:00")
def test_extract(
    db_uri: str,
    output_path: Path,
    s3_output_uri: str,
    expected_log: str,
    mocker: MockerFixture,
) -> None:
    """
    Test that extract logs the output path and calls extract_gp_practice
    """
    mock_logging_info = mocker.patch("pipeline.extract.logging.info")
    mock_extract_gp_practice = mocker.patch("pipeline.extract.extract_gp_practices")
    mock_store_local = mocker.patch("pipeline.extract.store_local")
    mock_store_s3 = mocker.patch("pipeline.extract.store_s3")

    extract(db_uri, output_path, s3_output_uri)

    if output_path:
        mock_store_local.assert_called()
        mock_store_s3.assert_not_called()
    if s3_output_uri:
        mock_store_s3.assert_called()
        mock_store_local.assert_not_called()

    mock_logging_info.assert_called_with(expected_log)
    mock_extract_gp_practice.assert_called_once_with(db_uri)


@freeze_time("2024-01-01 12:00:00")
def test_extract_gp_practice(mock_sql_data: Mock, mock_logging: Mock) -> None:
    """
    Test the extract_gp_practice function calls its dependencies with the correct arguments,
    and logs the expected messages.
    """
    extract_gp_practices(db_uri="test_db_uri")
    mock_sql_data.assert_has_calls(
        [
            call(QUERY_GP_PRACTICE, "test_db_uri"),
            call(QUERY_GP_ENDPOINTS, "test_db_uri"),
            call(QUERY_SERVICES_SIZE, "test_db_uri"),
            call(QUERY_SERVICES_COLUMNS, "test_db_uri"),
            call(QUERY_SERVICEENDPOINTS_COLUMNS, "test_db_uri"),
        ]
    )

    mock_logging.info.assert_has_calls(
        [
            call("Percentage of service profiles: 1.0%"),
            call("Percentage of all data fields: 11.9%"),
        ]
    )


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
                                "id": 1,
                                "endpointorder": 1,
                                "transport": "email",
                                "format": "PDF",
                                "interaction": "interaction1",
                                "businessscenario": "scenario1",
                                "address": "address1",
                                "comment": "comment1",
                                "iscompressionenabled": "false",
                            },
                            {
                                "id": 2,
                                "endpointorder": 2,
                                "transport": "sms",
                                "format": "XML",
                                "interaction": "interaction2",
                                "businessscenario": "scenario2",
                                "address": "address2",
                                "comment": "comment2",
                                "iscompressionenabled": "true",
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
                                "id": 1,
                                "endpointorder": 1,
                                "transport": "email",
                                "format": "PDF",
                                "interaction": "interaction1",
                                "businessscenario": "scenario1",
                                "address": "address1",
                                "comment": "comment1",
                                "iscompressionenabled": "false",
                            }
                        ],
                        [
                            {
                                "id": 2,
                                "endpointorder": 1,
                                "transport": "sms",
                                "format": "XML",
                                "interaction": "interaction2",
                                "businessscenario": "scenario2",
                                "address": "address2",
                                "comment": "comment2",
                                "iscompressionenabled": "true",
                            },
                            {
                                "id": 3,
                                "endpointorder": 2,
                                "transport": "fax",
                                "format": "TXT",
                                "interaction": "interaction3",
                                "businessscenario": "scenario3",
                                "address": "address3",
                                "comment": "comment3",
                                "iscompressionenabled": "false",
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
                                "id": 1,
                                "endpointorder": 1,
                                "transport": "email",
                                "format": "PDF",
                                "interaction": "interaction1",
                                "businessscenario": "scenario1",
                                "address": "address1",
                                "comment": "comment1",
                                "iscompressionenabled": "false",
                            }
                        ],
                        [
                            {
                                "id": 2,
                                "endpointorder": 1,
                                "transport": "sms",
                                "format": "XML",
                                "interaction": "interaction2",
                                "businessscenario": "scenario2",
                                "address": "address2",
                                "comment": "comment2",
                                "iscompressionenabled": "true",
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
                                "id": 1,
                                "endpointorder": 1,
                                "transport": "email",
                                "format": "PDF",
                                "interaction": "interaction1",
                                "businessscenario": "scenario1",
                                "address": "address1",
                                "comment": "comment1",
                                "iscompressionenabled": "false",
                            }
                        ],
                        [
                            {
                                "id": 2,
                                "endpointorder": 1,
                                "transport": "sms",
                                "format": "XML",
                                "interaction": "interaction2",
                                "businessscenario": "scenario2",
                                "address": "address2",
                                "comment": "comment2",
                                "iscompressionenabled": "true",
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
                                "id": 2,
                                "endpointorder": 1,
                                "transport": "sms",
                                "format": "XML",
                                "interaction": "interaction2",
                                "businessscenario": "scenario2",
                                "address": "address2",
                                "comment": "comment2",
                                "iscompressionenabled": "true",
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
                    "endpoints": [None],
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
