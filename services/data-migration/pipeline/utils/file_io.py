from enum import StrEnum

import awswrangler as wr
import pandas as pd
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import UtilsLogBase


class PathType(StrEnum):
    FILE = "file"
    S3 = "s3"


fileio_logger = Logger.get(service="fileio")


def read_parquet_file(path_type: PathType, file_path: str) -> pd.DataFrame:
    """
    Read a Parquet file into a DataFrame.
    """
    if path_type == PathType.S3:
        fileio_logger.log(UtilsLogBase.UTILS_FILEIO_001, file_path=file_path)
        return wr.s3.read_parquet(file_path, dataset=False)

    if path_type == PathType.FILE:
        fileio_logger.log(UtilsLogBase.UTILS_FILEIO_002, file_path=file_path)
        return pd.read_parquet(file_path)

    fileio_logger.log(UtilsLogBase.UTILS_FILEIO_003, path_type=path_type)
    raise ValueError()


def write_parquet_file(path_type: PathType, file_path: str, df: pd.DataFrame) -> None:
    """
    Write a DataFrame to a Parquet file.
    """
    if path_type == PathType.S3:
        fileio_logger.log(UtilsLogBase.UTILS_FILEIO_004, file_path=file_path)
        wr.s3.to_parquet(
            df=df,
            path=file_path,
            dataset=False,
            compression="snappy",
        )

    elif path_type == PathType.FILE:
        fileio_logger.log(UtilsLogBase.UTILS_FILEIO_005, file_path=file_path)
        df.to_parquet(
            file_path,
            engine="pyarrow",
            index=False,
            compression="snappy",
        )
    else:
        fileio_logger.log(UtilsLogBase.UTILS_FILEIO_006, file_path=file_path)
        raise ValueError()
