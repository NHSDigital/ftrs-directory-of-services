import pandas as pd
import pytest
from pytest_mock import MockerFixture

from pipeline.utils.file_io import PathType, read_parquet_file, write_parquet_file


def test_read_parquet_file_s3(mocker: MockerFixture) -> None:
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    file_path = "s3://bucket-name/path/to/file.parquet"

    mock_read_parquet = mocker.patch(
        "pipeline.utils.file_io.wr.s3.read_parquet",
        return_value=mock_df,
    )

    result = read_parquet_file(PathType.S3, file_path)

    mock_read_parquet.assert_called_once_with(file_path, dataset=False)
    pd.testing.assert_frame_equal(result, mock_df)


def test_read_parquet_file_local(mocker: MockerFixture) -> None:
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    file_path = "/path/to/file.parquet"

    mock_read_parquet = mocker.patch(
        "pipeline.utils.file_io.pd.read_parquet",
        return_value=mock_df,
    )

    result = read_parquet_file(PathType.FILE, file_path)

    mock_read_parquet.assert_called_once_with(file_path)
    pd.testing.assert_frame_equal(result, mock_df)


def test_read_parquet_file_invalid_path_type() -> None:
    file_path = "/path/to/file.parquet"

    with pytest.raises(ValueError, match="Unsupported path type: invalid"):
        read_parquet_file("invalid", file_path)


def test_write_parquet_file_s3(mocker: MockerFixture) -> None:
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    file_path = "s3://bucket-name/path/to/file.parquet"

    mock_write_parquet = mocker.patch(
        "pipeline.utils.file_io.wr.s3.to_parquet",
    )

    write_parquet_file(PathType.S3, file_path, mock_df)

    mock_write_parquet.assert_called_once_with(
        df=mock_df,
        path=file_path,
        dataset=False,
        compression="zstd",
    )


def test_write_parquet_file_local(mocker: MockerFixture) -> None:
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    file_path = "/path/to/file.parquet"

    mock_write_parquet = mocker.patch(
        "pipeline.utils.file_io.pd.DataFrame.to_parquet",
    )

    write_parquet_file(PathType.FILE, file_path, mock_df)

    mock_write_parquet.assert_called_once_with(
        file_path,
        engine="pyarrow",
        index=False,
        compression="zstd",
    )


def test_write_parquet_file_invalid_path_type() -> None:
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    file_path = "/path/to/file.parquet"

    with pytest.raises(ValueError, match="Unsupported path type: invalid"):
        write_parquet_file("invalid", file_path, mock_df)
