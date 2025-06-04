from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import UtilsLogBase
from typer import BadParameter

from pipeline.utils.file_io import PathType

validators_logger = Logger.get(service="validators")


def check_bucket_access(bucket_name: str) -> bool:
    """
    Check if an S3 bucket exists.

    :param bucket_name: Name of the S3 bucket to check.
    :return: True if the bucket exists, False otherwise.
    """

    s3_client = boto3.client("s3")
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        validators_logger.log(UtilsLogBase.UTILS_VALIDATOR_001, bucket_name=bucket_name)
    except ClientError as e:
        validators_logger.log(
            UtilsLogBase.UTILS_VALIDATOR_002, bucket_name=bucket_name, e=e
        )
        return False

    return True


def check_object_exists(bucket_name: str, object_key: str) -> bool:
    """
    Check if an S3 object exists.

    :param bucket_name: Name of the S3 bucket.
    :param object_key: Key of the S3 object.
    :return: True if the object exists, False otherwise.
    """
    s3_client = boto3.client("s3")
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_key)
        validators_logger.log(
            UtilsLogBase.UTILS_VALIDATOR_003,
            object_key=object_key,
            bucket_name=bucket_name,
        )
    except ClientError as e:
        validators_logger.log(
            UtilsLogBase.UTILS_VALIDATOR_004,
            object_key=object_key,
            bucket_name=bucket_name,
            e=e,
        )
        return False

    return True


def validate_s3_uri(
    s3_uri: str, should_file_exist: bool | None = None
) -> str | Literal[False]:
    """
    Validate and parse the S3 URI.
    """
    parsed = urlparse(s3_uri)
    if parsed.scheme != "s3":
        return False

    if not check_bucket_access(parsed.netloc):
        validators_logger.log(UtilsLogBase.UTILS_VALIDATOR_005, s3_uri=s3_uri)
        err_msg = UtilsLogBase.UTILS_VALIDATOR_005.value.message.format(s3_uri=s3_uri)
        raise BadParameter(err_msg)

    if should_file_exist is None:
        return s3_uri

    file_exists = check_object_exists(parsed.netloc, parsed.path.lstrip("/"))

    if should_file_exist and not file_exists:
        err_msg = f"File does not exist in S3: {s3_uri}. Please provide a valid S3 URI to an existing file."
        raise BadParameter(err_msg)

    if not should_file_exist and file_exists:
        validators_logger.log(UtilsLogBase.UTILS_VALIDATOR_007, s3_uri=s3_uri)
        err_msg = UtilsLogBase.UTILS_VALIDATOR_007.value.message.format(s3_uri=s3_uri)
        raise BadParameter(err_msg)

    return s3_uri


def validate_local_path(path: str, should_file_exist: bool | None = None) -> Path:
    """
    Validate the local path.
    """
    parsed_path = Path(path)

    if not parsed_path.parent.exists():
        parsed_path_parent = parsed_path.parent
        validators_logger.log(
            UtilsLogBase.UTILS_VALIDATOR_008, parsed_path_parent=parsed_path_parent
        )
        err_msg = UtilsLogBase.UTILS_VALIDATOR_008.value.message.format(
            parsed_path_parent=parsed_path_parent
        )
        raise BadParameter(err_msg)

    if should_file_exist is None:
        return parsed_path

    if should_file_exist and not parsed_path.is_file():
        validators_logger.log(UtilsLogBase.UTILS_VALIDATOR_009, parsed_path=parsed_path)
        err_msg = UtilsLogBase.UTILS_VALIDATOR_009.value.message.format(
            parsed_path=parsed_path
        )
        raise BadParameter(err_msg)

    if not should_file_exist and parsed_path.exists():
        validators_logger.log(UtilsLogBase.UTILS_VALIDATOR_010, parsed_path=parsed_path)
        err_msg = UtilsLogBase.UTILS_VALIDATOR_010.value.message.format(
            parsed_path=parsed_path
        )
        raise BadParameter(err_msg)

    return parsed_path


def validate_path(
    s3_or_local_path: str, *, should_file_exist: bool | None = None
) -> tuple[PathType.S3, str] | tuple[PathType.FILE, Path]:
    """
    Validate the output path for the extracted data.
    """
    if path := validate_s3_uri(s3_or_local_path, should_file_exist):
        return PathType.S3, path

    path = validate_local_path(s3_or_local_path, should_file_exist)
    return PathType.FILE, path
