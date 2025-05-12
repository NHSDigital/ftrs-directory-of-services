import json
import logging
from typing import Annotated

import numpy as np
import pandas as pd
from typer import Option

from pipeline.utils.db_config import DatabaseConfig
from pipeline.utils.dos_db import (
    get_gp_day_opening_times,
    get_gp_endpoints,
    get_gp_practices,
    get_gp_specified_opening_times,
    get_serviceendpoints_columns_count,
    get_services_columns_count,
    get_services_size,
)
from pipeline.utils.file_io import (
    write_parquet_file,
)
from pipeline.utils.secret_utils import get_secret
from pipeline.utils.validators import validate_path


def format_endpoints(gp_practice_endpoints: pd.DataFrame) -> pd.DataFrame:
    """Format the endpoints DataFrame."""
    endpoint_columns = [
        "id",
        "endpointorder",
        "transport",
        "format",
        "interaction",
        "businessscenario",
        "address",
        "comment",
        "iscompressionenabled",
    ]
    grouped_endpoints = gp_practice_endpoints.groupby("serviceid")[endpoint_columns]
    endpoint_data = (
        grouped_endpoints.apply(lambda group: group.to_dict(orient="records"))
        .reset_index()
        .rename(columns={0: "endpoints"})
    )

    return pd.DataFrame(
        data=endpoint_data,
        columns=["serviceid", "endpoints"],
    )


def format_openingtimes(
    day_opening_times: pd.DataFrame, specified_opening_times: pd.DataFrame
) -> dict:
    bank_holiday_df = day_opening_times[day_opening_times["dayOfWeek"] == "BankHoliday"]
    regular_days_df = day_opening_times[day_opening_times["dayOfWeek"] != "BankHoliday"]

    available_time_df = format_available_time(regular_days_df)
    available_time_public_holidays_df = format_bank_holidays(bank_holiday_df)
    available_time_variations_df = format_available_time_variations(
        specified_opening_times
    )
    not_available_df = format_not_available_time(specified_opening_times)

    availability = (
        available_time_df.merge(
            available_time_public_holidays_df,
            on="serviceid",
            how="outer",
            suffixes=("_available", "_public_holidays"),
        )
        .merge(
            available_time_variations_df,
            on="serviceid",
            how="outer",
            suffixes=("", "_variations"),
        )
        .merge(
            not_available_df,
            on="serviceid",
            how="outer",
            suffixes=("", "_not_available"),
        )
    )

    availability_combined = (
        availability.groupby(["serviceid"])[
            [
                "availableTime",
                "availableTimePublicHolidays",
                "availableTimeVariations",
                "notAvailable",
            ]
        ]
        .apply(
            lambda x: x.apply(
                lambda row: {
                    "availableTime": (row["availableTime"]),
                    "availableTimePublicHolidays": (row["availableTimePublicHolidays"]),
                    "availableTimeVariations": (row["availableTimeVariations"]),
                    "notAvailable": (row["notAvailable"]),
                },
                axis=1,
            )
        )
        .reset_index(name="availability")
    )

    return availability_combined


def format_available_time(service_day_opening_times: pd.DataFrame) -> dict:
    availableTime = (
        service_day_opening_times.groupby(["serviceid"])[
            ["dayOfWeek", "availableStartTime", "availableEndTime"]
        ]
        .apply(
            lambda x: x.apply(
                lambda row: {
                    "dayOfWeek": [row["dayOfWeek"][:3].lower()],
                    **(
                        {"allDay": True}
                        if row["availableStartTime"] == "00:00:00"
                        and row["availableEndTime"] == "23:59:00"
                        else {
                            "availableStartTime": row["availableStartTime"],
                            "availableEndTime": row["availableEndTime"],
                        }
                    ),
                },
                axis=1,
            ).tolist()
        )
        .reset_index(name="availableTime")
    )

    return availableTime


def format_bank_holidays(bank_holiday_df: pd.DataFrame) -> dict:
    availableTimePublicHolidays = (
        bank_holiday_df.groupby(["serviceid"])[
            ["availableStartTime", "availableEndTime"]
        ]
        .apply(
            lambda x: [
                {
                    "availableStartTime": x["availableStartTime"].iloc[0],
                    "availableEndTime": x["availableEndTime"].iloc[0],
                }
            ]
        )
        .reset_index(name="availableTimePublicHolidays")
    )

    return availableTimePublicHolidays


def format_available_time_variations(
    service_specified_opening_times: pd.DataFrame,
) -> dict:
    service_specified_opening_times["start"] = pd.to_datetime(
        service_specified_opening_times["date"].astype(str)
        + "T"
        + service_specified_opening_times["starttime"].astype(str),
        format="%Y-%m-%dT%H:%M:%S",
    )

    service_specified_opening_times["end"] = pd.to_datetime(
        service_specified_opening_times["date"].astype(str)
        + "T"
        + service_specified_opening_times["endtime"].astype(str),
        format="%Y-%m-%dT%H:%M:%S",
    )

    availableTimeVariations = (
        service_specified_opening_times.groupby(["serviceid", "date", "start"])
        .apply(
            lambda x: {
                "start": x["start"].iloc[0].strftime("%Y-%m-%dT%H:%M:%S").strip(),
                "end": x["end"].iloc[0].strftime("%Y-%m-%dT%H:%M:%S").strip(),
            },
        )
        .reset_index(name="groupedStartEnd")
    )

    availableTimeVariations["availableTimeVariations"] = (
        availableTimeVariations.groupby("serviceid")["groupedStartEnd"].transform(
            lambda x: [{"description": "special", "during": item} for item in x]
        )
    )

    availableTimeVariations = (
        availableTimeVariations.groupby(["serviceid"])["availableTimeVariations"]
        .apply(list)
        .reset_index()
    )

    return availableTimeVariations


def format_not_available_time(specified_opening_times: pd.DataFrame) -> dict:
    closed_times = specified_opening_times[specified_opening_times["isclosed"]]

    if len(closed_times) == 0:
        return pd.DataFrame(columns=["serviceid", "notAvailable"])

    # Convert the date and time columns to datetime
    closed_times["start"] = pd.to_datetime(
        closed_times["date"].astype(str) + "T" + closed_times["starttime"].astype(str),
        format="%Y-%m-%dT%H:%M:%S",
    )

    closed_times["end"] = pd.to_datetime(
        closed_times["date"].astype(str) + "T" + closed_times["endtime"].astype(str),
        format="%Y-%m-%dT%H:%M:%S",
    )

    notAvailable = (
        closed_times.groupby(["serviceid", "date", "start"])
        .apply(
            lambda x: {
                "start": x["start"].iloc[0].strftime("%Y-%m-%dT%H:%M:%S").strip(),
                "end": x["end"].iloc[0].strftime("%Y-%m-%dT%H:%M:%S").strip(),
            },
        )
        .reset_index(name="groupedStartEnd")
    )

    notAvailable["notAvailable"] = notAvailable.groupby("serviceid")[
        "groupedStartEnd"
    ].transform(lambda x: [{"description": "special", "during": item} for item in x])

    notAvailable = (
        notAvailable.groupby(["serviceid"])["notAvailable"].apply(list).reset_index()
    )

    return notAvailable


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
    # We use the no_silent_downcasting option, with replace and infer objects to ensure that all possible
    #   nullables are outputted as NoneTypes, and not NaN etc
    with pd.option_context("future.no_silent_downcasting", True):
        result = (
            gp_practice_df.merge(grouped_endpoints, on="serviceid", how="left")
            .replace([np.nan], [None])
            .infer_objects(copy=False)
        )

    # Force all null values in the endpoints column to be empty lists
    for row in result.loc[result.endpoints.isnull(), "endpoints"].index:
        result.at[row, "endpoints"] = []

    return result


def merge_gp_practice_with_openingtimes(
    gp_practice_df: pd.DataFrame, grouped_openingtimes: pd.DataFrame
) -> pd.DataFrame:
    # We use the no_silent_downcasting option, with replace and infer objects to ensure that all possible
    #   nullables are outputted as NoneTypes, and not NaN etc
    with pd.option_context("future.no_silent_downcasting", True):
        result = (
            gp_practice_df.merge(grouped_openingtimes, on="serviceid", how="left")
            .drop(columns=["serviceid"])
            .replace([np.nan], [None])
            .infer_objects(copy=False)
        )

    return result


def extract_gp_practices(db_uri: str) -> pd.DataFrame:
    gp_practice_df = get_gp_practices(db_uri)

    # Extract endpoint information
    gp_practice_endpoints_df = get_gp_endpoints(db_uri)
    grouped_endpoints = format_endpoints(gp_practice_endpoints_df)
    gp_practice_extract = merge_gp_practice_with_endpoints(
        gp_practice_df, grouped_endpoints
    )

    # Extract Opening Time information
    gp_practice_day_openingtime_df = get_gp_day_opening_times(db_uri)
    gp_practice_specified_openingtime_df = get_gp_specified_opening_times(db_uri)

    grouped_openingtimes = format_openingtimes(
        gp_practice_day_openingtime_df, gp_practice_specified_openingtime_df
    )

    gp_practice_extract = merge_gp_practice_with_openingtimes(
        gp_practice_extract, grouped_openingtimes
    )

    logging_gp_practice_metrics(gp_practice_extract, db_uri)
    return gp_practice_extract


def extract(
    db_uri: Annotated[str, Option(..., help="URI to connect to the source database")],
    output: Annotated[
        str,
        Option(..., help="S3 URI or file path to save the extracted data"),
    ],
) -> None:
    """
    Extract GP practice data from the source database and save it to the specified path.
    """
    path_type, output_path = validate_path(output, should_file_exist=False)

    logging.info(f"Extracting data to {output_path}")
    extract_gp_practice_df = extract_gp_practices(db_uri)

    write_parquet_file(path_type, output_path, extract_gp_practice_df)
    logging.info("Data extraction completed successfully.")


def lambda_handler(event: dict, context: object) -> dict[str, any] | None:
    """
    AWS Lambda handler function.
    Parameters:
    - event: dict, contains the event data passed to the function.
    - context: object, provides runtime information to the handler.
    Returns:
    - dict: Response object with status code and body.
    """
    print("Received event:", json.dumps(event))

    db_credentials = get_secret(
        DatabaseConfig.source_db_credentials(), transform="json"
    )
    db_config = DatabaseConfig(**db_credentials)

    extract(
        db_config.connection_string,
        output=event["s3_output_uri"],
    )
