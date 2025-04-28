from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel
from typer import BadParameter

from pipeline.utils.file_io import PathType
import boto3
from botocore.exceptions import ClientError
import logging
from typing import Literal


class S3Path(BaseModel):
    bucket: str
    key: str


def check_bucket_access(bucket_name: str) -> bool:
    """
    Check if an S3 bucket exists.

    :param bucket_name: Name of the S3 bucket to check.
    :return: True if the bucket exists, False otherwise.
    """

    s3_client = boto3.client("s3")
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logging.info(f"Bucket {bucket_name} exists and is accessible.")
    except ClientError as e:
        logging.error(f"Error checking bucket {bucket_name}: {e}")
        return False

    return True


def validate_s3_uri(s3_uri: str) -> str | Literal[False]:
    """
    Validate and parse the S3 URI.
    """
    parsed = urlparse(s3_uri)
    if parsed.scheme != "s3":
        return False

    if not check_bucket_access(parsed.netloc):
        err_msg = f"Invalid S3 URI: {s3_uri}. Please provide a valid S3 URI and confirm you have access to the S3 bucket."
        raise BadParameter(err_msg)

    return s3_uri


def validate_local_path(path: str) -> Path:
    """
    Validate the local path.
    """
    parsed_path = Path(path)
    if not parsed_path.parent.exists():
        err_msg = f"Parent directory does not exist: {parsed_path.parent}. Please provide a valid path."
        raise BadParameter(err_msg)

    return parsed_path


def validate_path(
    s3_or_local_path: str,
) -> tuple[PathType.S3, S3Path] | tuple[PathType.FILE, Path]:
    """
    Validate the output path for the extracted data.
    """
    if path := validate_s3_uri(s3_or_local_path):
        return PathType.S3, path

    if path := validate_local_path(s3_or_local_path):
        return PathType.FILE, path

    err_msg = f"Invalid path: {s3_or_local_path}. Please provide a valid S3 URI or a local file path."
    raise BadParameter(err_msg)
