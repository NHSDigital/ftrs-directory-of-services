from pathlib import Path

import pandas as pd
import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from pipeline.transform import transform
from pipeline.utils.file_io import PathType
from tests.util.stub_data import (
    extracted_GP_Practice,
    mock_gp_endpoint_json_dump_B,
    mock_gp_endpoint_json_dump_C,
    mock_gp_endpoints_formatted_B,
    mock_gp_endpoints_formatted_C,
    transformed_GP_Practice_HS,
    transformed_GP_Practice_Org,
)


@freeze_time("2025-03-27 12:00:00")
@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        (
            # Input data
            pd.DataFrame(extracted_GP_Practice),
            # Expected output
            pd.DataFrame(
                {
                    "organisation": [transformed_GP_Practice_Org],
                    "healthcare-service": [transformed_GP_Practice_HS],
                }
            ),
        ),
        (
            # Input data with multiple endpoints and varied compression settings
            pd.DataFrame(
                dict(
                    {
                        k: [v]
                        for k, v in extracted_GP_Practice.items()
                        if k != "endpoints"
                    },
                    endpoints=[
                        [mock_gp_endpoints_formatted_B, mock_gp_endpoints_formatted_C]
                    ],
                ),
            ),
            # Expected output
            pd.DataFrame(
                {
                    "organisation": [
                        dict(
                            {
                                k: v
                                for k, v in transformed_GP_Practice_Org.items()
                                if k != "endpoints"
                            },
                            endpoints=[
                                mock_gp_endpoint_json_dump_B,
                                mock_gp_endpoint_json_dump_C,
                            ],
                        )
                    ],
                    "healthcare-service": [transformed_GP_Practice_HS],
                },
            ),
        ),
        (
            # Input data where endpoints is none
            pd.DataFrame(
                dict(
                    {
                        k: [v]
                        for k, v in extracted_GP_Practice.items()
                        if k != "endpoints"
                    },
                    endpoints=[[]],
                ),
            ),
            # Expected output
            pd.DataFrame(
                {
                    "organisation": [
                        dict(
                            {
                                k: v
                                for k, v in transformed_GP_Practice_Org.items()
                                if k != "endpoints"
                            },
                            endpoints=[],
                        )
                    ],
                    "healthcare-service": [transformed_GP_Practice_HS],
                }
            ),
        ),
    ],
)
def test_transform(
    mocker: MockerFixture,
    input_data: pd.DataFrame,
    expected_output: pd.DataFrame,
    mock_tmp_directory: Path,
) -> None:
    """
    Test the transform function to ensure input data is transformed correctly.
    """
    input_path = mock_tmp_directory / "input.parquet"
    output_path = mock_tmp_directory / "output.parquet"

    input_path.touch()

    assert input_path.exists()
    assert not output_path.exists()

    read_mock = mocker.patch(
        "pipeline.transform.read_parquet_file", return_value=input_data
    )
    mocker.patch(
        "ftrs_data_layer.models.uuid4",
        return_value="123e4567-e89b-12d3-a456-42661417400a",
    )
    write_mock = mocker.patch("pipeline.transform.write_parquet_file")

    transform(input=str(input_path), output=str(output_path))

    read_mock.assert_called_once_with(PathType.FILE, input_path)
    write_mock.assert_called_once()

    file_type, file_path, gp_practice_df = write_mock.call_args[0]

    assert file_type == PathType.FILE
    assert file_path == output_path
    assert isinstance(gp_practice_df, pd.DataFrame)
    assert not gp_practice_df.empty
    assert gp_practice_df.shape[0] == expected_output.shape[0], "Row count mismatch"

    for idx, row in gp_practice_df.iterrows():
        row_dict = row.to_dict()
        expected_row_dict = expected_output.iloc[idx].to_dict()

        assert row_dict == expected_row_dict, (
            f"Row {idx} mismatch: {row_dict} != {expected_row_dict}"
        )


def test_transform_empty_dataframe(
    mocker: MockerFixture, mock_tmp_directory: Path
) -> None:
    """
    Test the transform function with an empty DataFrame.
    """
    input_path = mock_tmp_directory / "mock_input_path"
    output_path = mock_tmp_directory / "mock_output_path"
    input_path.touch()

    mocker.patch("pipeline.transform.read_parquet_file", return_value=pd.DataFrame())

    with pytest.raises(ValueError) as excinfo:
        transform(input=str(input_path), output=str(output_path))

    assert str(excinfo.value) == "No data found in the input DataFrame"


def test_read_s3(
    mocker: MockerFixture,
    mock_tmp_directory: Path,
) -> None:
    mock_bucket_access = mocker.patch(
        "pipeline.utils.validators.check_bucket_access", return_value=True
    )
    mock_check_object = mocker.patch(
        "pipeline.utils.validators.check_object_exists", return_value=True
    )
    mock_read = mocker.patch(
        "pipeline.transform.read_parquet_file", return_value=pd.DataFrame()
    )
    mocker.patch("pipeline.transform.transform_gp_practices")

    output_path = mock_tmp_directory / "output.parquet"
    s3_uri = "s3://your-bucket-name/path/to/object/input.parquet"

    transform(input=str(s3_uri), output=str(output_path))

    mock_read.assert_called_once_with(PathType.S3, s3_uri)

    mock_bucket_access.assert_called_once_with("your-bucket-name")
    mock_check_object.assert_called_once_with(
        "your-bucket-name", "path/to/object/input.parquet"
    )


def test_write_s3(
    mocker: MockerFixture,
    mock_tmp_directory: Path,
) -> None:
    mock_bucket_access = mocker.patch(
        "pipeline.utils.validators.check_bucket_access", return_value=True
    )
    mock_check_object = mocker.patch(
        "pipeline.utils.validators.check_object_exists", return_value=False
    )

    mock_read = mocker.patch(
        "pipeline.transform.read_parquet_file", return_value=pd.DataFrame()
    )
    mock_write = mocker.patch("pipeline.transform.write_parquet_file")
    mocker.patch("pipeline.transform.transform_gp_practices", return_value="TestOutput")

    input_path = mock_tmp_directory / "input.parquet"
    input_path.touch()

    s3_uri = "s3://your-bucket-name/path/to/object/output.parquet"

    transform(input=str(input_path), output=str(s3_uri))

    mock_bucket_access.assert_called_once_with("your-bucket-name")
    mock_check_object.assert_called_once_with(
        "your-bucket-name", "path/to/object/output.parquet"
    )

    mock_read.assert_called_once_with(PathType.FILE, input_path)
    mock_write.assert_called_once_with(PathType.S3, s3_uri, "TestOutput")
