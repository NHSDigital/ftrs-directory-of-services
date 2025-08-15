"""
Table Export Utilities

Utilities for exporting data from DynamoDB tables to parquet files in S3.
These are designed to be run **only** locally or via GitHub Actions.
These should not be used in Lambda code due to rich formatting of outputs.
"""

import asyncio
import gzip
import json
import time
from concurrent.futures import ThreadPoolExecutor
from math import floor
from threading import Lock

import boto3
import pandas as pd
import rich
from ftrs_common.utils.db_service import format_table_name
from ftrs_data_layer.client import get_dynamodb_client
from mypy_boto3_dynamodb.type_defs import ExportDescriptionTypeDef

CONSOLE = rich.get_console()
S3_CLIENT = boto3.client("s3")


def get_s3_bucket_name(env: str, workspace: str | None = None) -> str:
    """
    Get the data migration pipeline store S3 bucket name
    """
    bucket_name = f"ftrs-dos-{env}-data-migration-pipeline-store"
    if workspace:
        bucket_name += f"-{workspace}"

    return bucket_name


def get_table_arn(table_name: str) -> str:
    """
    Get the ARN of a DynamoDB table
    """
    client = get_dynamodb_client()
    response = client.describe_table(TableName=table_name)
    return response["Table"]["TableArn"]


def trigger_table_export(
    table_name: str,
    s3_bucket_name: str,
) -> ExportDescriptionTypeDef:
    """
    Trigger an export of a DynamoDB table to S3
    """
    client = get_dynamodb_client()

    table_arn = get_table_arn(table_name)
    response = client.export_table_to_point_in_time(
        TableArn=table_arn,
        S3Bucket=s3_bucket_name,
        S3Prefix=f"exports/{table_name}/",
    )

    return response["ExportDescription"]


def is_export_complete(export_arn: str) -> bool:
    """
    Check if an export is complete.

    Return (False, status) if the status is IN_PROGRESS or QUEUED.
    Return (True, status) if the status is COMPLETED.
    Throw an error if the status is anything else.
    """
    client = get_dynamodb_client()

    response = client.describe_export(ExportArn=export_arn)
    status = response["ExportDescription"]["ExportStatus"]

    if status in ["IN_PROGRESS", "QUEUED"]:
        return False

    if status == "COMPLETED":
        return True

    raise ValueError(f"Unexpected export status: {status}")


async def export_table(
    entity_name: str,
    env: str,
    workspace: str | None = None,
) -> ExportDescriptionTypeDef:
    """
    Export a DynamoDB table to S3.
    """
    table_name = format_table_name(entity_name, env, workspace)
    s3_bucket = get_s3_bucket_name(env, workspace)

    response = trigger_table_export(table_name, s3_bucket)
    export_arn = response["ExportArn"]

    CONSOLE.log(
        f"Triggered export of [bright_blue]{table_name}[/bright_blue] to S3 bucket [bright_cyan]{response['S3Bucket']}[/bright_cyan]"
    )

    time_start = time.monotonic()

    while not is_export_complete(export_arn):
        await asyncio.sleep(10)
        time_elapsed_seconds = floor(time.monotonic() - time_start)

        CONSOLE.log(
            f"Waiting for [bright_blue]{table_name}[/bright_blue] export to complete [bright_black]({time_elapsed_seconds}s)[/bright_black]",
        )

    CONSOLE.log(
        f"Export of [bright_blue]{table_name}[/bright_blue] completed successfully",
        style="green",
    )
    client = get_dynamodb_client()
    return client.describe_export(ExportArn=export_arn)["ExportDescription"]


async def process_export(description: ExportDescriptionTypeDef) -> None:
    """
    Process the compressed export files into a single parquet file.
    """
    file_list = get_export_file_list(description)
    compressed_files = download_export_files(description, file_list)
    records = decompress_and_parse_files(compressed_files)
    return pd.DataFrame(records, columns=["data"])


def get_export_file_list(description: ExportDescriptionTypeDef) -> list[dict]:
    """
    Get the list of data files from the export manifest files
    """
    manifest_obj = S3_CLIENT.get_object(
        Bucket=description["S3Bucket"],
        Key=description["ExportManifest"],
    )
    manifest = json.loads(manifest_obj["Body"].read().decode("utf-8"))

    manifest_files_obj = S3_CLIENT.get_object(
        Bucket=description["S3Bucket"],
        Key=manifest["manifestFilesS3Key"],
    )
    return [
        json.loads(line)
        for line in manifest_files_obj["Body"].read().decode("utf-8").splitlines()
        if line.strip()
    ]


def download_export_files(
    description: ExportDescriptionTypeDef, file_list: list[dict]
) -> list[bytes]:
    """
    Download the exported files from S3.
    """
    table_name = description["TableArn"].rsplit("/")[-1]
    files_lock = Lock()
    files = []

    CONSOLE.log(
        f"Downloading {len(file_list)} data files for [bright_blue]{table_name}[/bright_blue]",
        style="bright_black",
    )

    def _download_file(index: int, file_info: dict) -> bytes:
        obj = S3_CLIENT.get_object(
            Bucket=description["S3Bucket"],
            Key=file_info["dataFileS3Key"],
        )
        with files_lock:
            files.append(obj["Body"].read())

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda tuple: _download_file(*tuple), enumerate(file_list))

    return files


def decompress_and_parse_files(compressed_files: list[bytes]) -> list[dict]:
    """
    Decompress and parse the exported files.
    """
    CONSOLE.log(
        f"Decompressing {len(compressed_files)} data files",
        style="bright_black",
    )

    records = []
    for idx, file_content in enumerate(compressed_files):
        decompressed_content = gzip.decompress(file_content)
        file_records = [
            line
            for line in decompressed_content.decode("utf-8").splitlines()
            if line.strip()
        ]
        records.extend(file_records)
        CONSOLE.log(
            f"Parsed {len(file_records)} records from file [bright_cyan]{idx + 1}[/bright_cyan]",
            style="bright_black",
        )

    return records
