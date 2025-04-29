import logging
from enum import StrEnum

import awswrangler as wr
import pandas as pd


class PathType(StrEnum):
    FILE = "file"
    S3 = "s3"


def read_parquet_file(path_type: PathType, file_path: str) -> pd.DataFrame:
    """
    Read a Parquet file into a DataFrame.
    """
    if path_type == PathType.S3:
        logging.info(f"Reading from S3 path: {file_path}")
        return wr.s3.read_parquet(file_path, dataset=False)

    if path_type == PathType.FILE:
        logging.info(f"Reading from local file path: {file_path}")
        return pd.read_parquet(file_path)

    err_msg = f"Unsupported path type: {path_type}"
    raise ValueError(err_msg)


def write_parquet_file(path_type: PathType, file_path: str, df: pd.DataFrame) -> None:
    """
    Write a DataFrame to a Parquet file.
    """
    if path_type == PathType.S3:
        logging.info(f"Writing to S3 path: {file_path}")
        wr.s3.to_parquet(
            df=df,
            path=file_path,
            dataset=False,
            compression="zstd",
        )

    elif path_type == PathType.FILE:
        logging.info(f"Writing to local file path: {file_path}")
        df.to_parquet(
            file_path,
            engine="pyarrow",
            index=False,
            compression="zstd",
        )
    else:
        err_msg = f"Unsupported path type: {path_type}"
        raise ValueError(err_msg)
