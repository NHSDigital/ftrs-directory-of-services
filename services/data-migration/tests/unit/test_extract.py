from pathlib import Path
from unittest import mock
from unittest.mock import Mock, call

import pandas as pd
import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from pipeline.extract import (
    extract,
    extract_gp_practices,
    format_endpoints,
    lambda_handler,
    merge_gp_practice_with_endpoints,
)
from pipeline.utils.dos_db import (
    QUERY_GP_ENDPOINTS,
    QUERY_GP_PRACTICE,
    QUERY_SERVICEENDPOINTS_COLUMNS,
    QUERY_SERVICES_COLUMNS,
    QUERY_SERVICES_SIZE,
)
from pipeline.utils.file_io import PathType
from tests.util.stub_data import (
    mock_gp_endpoints_A,
    mock_gp_endpoints_B,
    mock_gp_endpoints_C,
    mock_gp_endpoints_formatted_A,
    mock_gp_endpoints_formatted_B,
    mock_gp_endpoints_formatted_C,
    mock_gp_practices_A,
    mock_gp_practices_B,
    mock_gp_practices_df,
    mock_two_gp_practices_df,
)


@pytest.mark.parametrize(
    "db_uri, output_path, expected_path_type",
    [
        ("test_db_uri", "input-file.parquet", PathType.FILE),
        ("test_db_uri", "s3://test_s3_output_uri/input-file.parquet", PathType.S3),
    ],
)
@freeze_time("2024-01-01 12:00:00")
def test_extract(
    db_uri: str,
    output_path: str,
    expected_path_type: PathType,
    mocker: MockerFixture,
    mock_tmp_directory: Path,
) -> None:
    """
    Test that extract logs the output path and calls extract_gp_practice
    """
    mock_extract_gp_practice = mocker.patch(
        "pipeline.extract.extract_gp_practices", return_value=mock_gp_practices_df
    )
    mock_write_parquet = mocker.patch("pipeline.extract.write_parquet_file")
    mock_check_bucket = mocker.patch(
        "pipeline.utils.validators.check_bucket_access", return_value=True
    )

    if expected_path_type == PathType.FILE:
        output_path = mock_tmp_directory / output_path

    extract(db_uri, str(output_path))

    mock_extract_gp_practice.assert_called_once_with(db_uri)
    mock_write_parquet.assert_called_once_with(
        expected_path_type,
        output_path,
        mock_gp_practices_df,
    )

    if expected_path_type == PathType.S3:
        mock_check_bucket.assert_called_once_with(output_path.split("/")[2])


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
            call("Percentage of all data fields: 33.33%"),
        ]
    )


@pytest.mark.parametrize(
    "input_df, expected_df",
    [
        (
            pd.DataFrame(
                dict(
                    {
                        key: [mock_gp_endpoints_A[key], mock_gp_endpoints_B[key]]
                        for key in mock_gp_endpoints_A.keys()
                        if key != "serviceid"
                    },
                    serviceid=[1, 1],  # both endpoints use same service id for test
                )
            ),
            pd.DataFrame(
                {
                    "serviceid": [1],
                    "endpoints": [
                        [
                            mock_gp_endpoints_formatted_A,
                            mock_gp_endpoints_formatted_B,
                        ]
                    ],
                }
            ),
        ),
        (
            pd.DataFrame(
                dict(
                    {
                        key: [
                            mock_gp_endpoints_A[key],
                            mock_gp_endpoints_B[key],
                            mock_gp_endpoints_C[key],
                        ]
                        for key in mock_gp_endpoints_A.keys()
                        if key != "serviceid"
                    },
                    serviceid=[1, 2, 2],  # test we get single and double
                )
            ),
            pd.DataFrame(
                {
                    "serviceid": [1, 2],
                    "endpoints": [
                        [mock_gp_endpoints_formatted_A],
                        [mock_gp_endpoints_formatted_B, mock_gp_endpoints_formatted_C],
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
            pd.DataFrame(
                {
                    "serviceid": [1],
                    "endpoints": [[mock_gp_endpoints_formatted_A]],
                }
            ),
            pd.DataFrame(
                dict(
                    {
                        k: [v]
                        for k, v in mock_gp_practices_A.items()
                        if k != "serviceid"
                    },
                    endpoints=[[mock_gp_endpoints_formatted_A]],
                )
            ),
        ),
        (
            mock_two_gp_practices_df,
            pd.DataFrame(
                {
                    "serviceid": [1, 2],
                    "endpoints": [
                        [mock_gp_endpoints_formatted_A],
                        [mock_gp_endpoints_formatted_B],
                    ],
                }
            ),
            pd.DataFrame(
                dict(
                    {
                        key: [mock_gp_practices_A[key], mock_gp_practices_B[key]]
                        for key in mock_gp_practices_A.keys()
                        if key != "serviceid"
                    },  # Remove service id
                    endpoints=[
                        [mock_gp_endpoints_formatted_A],
                        [mock_gp_endpoints_formatted_B],
                    ],  # add on endpoints column
                )
            ),
        ),
        (
            mock_gp_practices_df,
            pd.DataFrame(
                {
                    "serviceid": [2],
                    "endpoints": [[mock_gp_endpoints_formatted_A]],
                }
            ),
            pd.DataFrame(
                dict(
                    {
                        k: [v]
                        for k, v in mock_gp_practices_A.items()
                        if k != "serviceid"
                    },  # Remove service id
                    endpoints=[[]],  # add on endpoints column
                )
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
    pd.testing.assert_frame_equal(result, expected_df)


def test_lambda_handler_successful_execution(mocker: MockerFixture) -> None:
    """
    Test that the lambda handler executes successfully
    """
    event = {"s3_output_uri": "s3://bucket/output"}
    context = mock.Mock()

    mocker.patch(
        "pipeline.extract.get_secret",
        return_value={
            "host": "localhost",
            "port": 5432,
            "username": "username",
            "password": "password",
            "dbname": "db",
        },
    )
    mock_extract = mocker.patch("pipeline.extract.extract")

    response = lambda_handler(event, context)

    mock_extract.assert_called_once_with(
        "postgresql://username:password@localhost:5432/db",
        output="s3://bucket/output",
    )
    assert response is None
