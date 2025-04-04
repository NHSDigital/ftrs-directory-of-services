import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path

import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from pipeline.db_utils import (
    get_gp_endpoints,
    get_gp_practices,
    get_serviceendpoints_columns_count,
    get_services_columns_count,
    get_services_size,
)
from pipeline.exceptions import ExtractArgsError, InvalidS3URI, S3BucketAccessError


def format_endpoints(gp_practice_endpoints: pd.DataFrame) -> pd.DataFrame:
    # combining all the endpoint columns into one column
    return (
        gp_practice_endpoints.groupby(["serviceid"])[
            [
                "id",
                "endpointorder",
                "transport",
                "format",
                "interaction",
                "businessscenario",
                "address",
                "comment",
                "iscompressionenabled",
                "serviceid",
            ]
        ]
        .apply(
            lambda x: x.apply(
                lambda row: {
                    "endpointid": row["id"],
                    "endpointorder": row["endpointorder"],
                    "transport": row["transport"],
                    "format": row["format"],
                    "interaction": row["interaction"],
                    "businessscenario": row["businessscenario"],
                    "address": row["address"],
                    "comment": row["comment"],
                    "iscompressionenabled": row["iscompressionenabled"],
                    "serviceid": row["serviceid"],
                },
                axis=1,
            ).tolist()
        )
        .reset_index(name="endpoints")
    )


def calculate_service_profiles_percentage(
    gp_practice_extract_size: int, services_size: int
) -> float:
    return round(gp_practice_extract_size / services_size * 100, 2)


def calculate_data_fields_percentage(
    gp_practice_extract_column: int,
    services_columns: int,
    serviceendpoints_columns: int,
) -> float:
    return round(
        gp_practice_extract_column
        / (services_columns + serviceendpoints_columns)
        * 100,
        2,
    )


def logging_gp_practice_metrics(gp_practice_extract: pd.DataFrame, db_uri: str) -> None:
    services_size = get_services_size(db_uri)
    gp_practice_extract_size = len(gp_practice_extract)
    service_profiles_percentage = calculate_service_profiles_percentage(
        gp_practice_extract_size, services_size
    )

    services_columns = get_services_columns_count(db_uri)
    serviceendpoints_columns = get_serviceendpoints_columns_count(db_uri)
    gp_practice_extract_column = gp_practice_extract.shape[1]
    data_fields_percentage = calculate_data_fields_percentage(
        gp_practice_extract_column, services_columns, serviceendpoints_columns
    )

    logging.info(f"Percentage of service profiles: {service_profiles_percentage}%")
    logging.info(f"Percentage of all data fields: {data_fields_percentage}%")


def merge_gp_practice_with_endpoints(
    gp_practice_df: pd.DataFrame, grouped_endpoints: pd.DataFrame
) -> pd.DataFrame:
    return gp_practice_df.merge(grouped_endpoints, on="serviceid", how="left").drop(
        columns=["serviceid"]
    )


def extract_gp_practice(db_uri: str) -> pd.DataFrame:
    gp_practice_df = get_gp_practices(db_uri)
    gp_practice_endpoints_df = get_gp_endpoints(db_uri)

    grouped_endpoints = format_endpoints(gp_practice_endpoints_df)
    gp_practice_extract = merge_gp_practice_with_endpoints(
        gp_practice_df, grouped_endpoints
    )
    logging_gp_practice_metrics(gp_practice_extract, db_uri)
    return gp_practice_extract


def store_local(
    gp_practice_extract: pd.DataFrame,
    output_path: Path,
    clone_timestamp: str,
    extract_name: str,
) -> None:
    gp_practice_extract.to_parquet(
        output_path / f"{extract_name}-{clone_timestamp}.parquet",
        engine="pyarrow",
        index=False,
        compression="zstd",
    )


def convert_to_parquet_buffer(gp_practice_extract: pd.DataFrame) -> BytesIO:
    buffer = BytesIO()
    table = pa.Table.from_pandas(gp_practice_extract)
    pq.write_table(table, buffer)
    return buffer


def extract_s3_details(s3_output_uri: str) -> tuple[str, str]:
    bucket_name = s3_output_uri.split("/")[2]
    path = s3_output_uri.split("/")[3:]
    path = "/".join(path).removesuffix("/")
    return bucket_name, path


def upload_to_s3(buffer: BytesIO, bucket_name: str, path: str) -> None:
    s3 = boto3.client("s3")
    file_name = "dos-gp-practice-extract.parquet"
    key_name = f"{path}/{file_name}"
    s3.put_object(Bucket=bucket_name, Key=key_name, Body=buffer.getvalue())
    s3.close()


def store_s3(gp_practice_extract: pd.DataFrame, s3_output_uri: str) -> None:
    buffer = convert_to_parquet_buffer(gp_practice_extract)
    bucket_name, path = extract_s3_details(s3_output_uri)
    upload_to_s3(buffer, bucket_name, path)


def extract(db_uri: str, output_path: Path = None, s3_output_uri: str = None) -> None:
    extract_gp_practice_df = extract_gp_practice(db_uri)
    clone_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    if output_path:
        logging.info(f"Extracting data to {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
        store_local(
            extract_gp_practice_df,
            output_path,
            clone_timestamp,
            "dos-gp-practice-extract",
        )
    if s3_output_uri:
        logging.info(f"Extracting data to {s3_output_uri}")
        store_s3(extract_gp_practice_df, s3_output_uri)


def validate_s3_uri(uri: str) -> str:
    if not uri.startswith("s3://"):
        raise InvalidS3URI(uri)

    try:
        s3 = boto3.client("s3")
        bucket_name = uri.split("/")[2]
        response = s3.head_bucket(Bucket=bucket_name)
        logging.info(
            f"Bucket {bucket_name} has status {response['ResponseMetadata']['HTTPStatusCode']}"
        )
        s3.close()
    except Exception:
        raise S3BucketAccessError()

    return uri


def main(args: list[str] | None = None) -> None:
    import argparse

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(description="Extract data from source")
    parser.add_argument(
        "--db-uri", type=str, required=True, help="URI to connect to the database"
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        required=False,
        help="Path to save the extracted data locally",
    )
    parser.add_argument(
        "--s3-output-uri",
        type=validate_s3_uri,
        required=False,
        help="Path to save the extracted data in s3, in the format s3://<s3_bucket_name>/<s3_bucket_path>",
    )

    args = parser.parse_args(args)

    if args.db_uri and (bool(args.output_path) ^ bool(args.s3_output_uri)):
        extract(args.db_uri, args.output_path, args.s3_output_uri)
    else:
        raise ExtractArgsError()
