import numpy as np
import pandas as pd


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
    service_specified_opening_times = service_specified_opening_times[
        ~service_specified_opening_times["isclosed"]
    ]

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
    closed_times["unavailableDate"] = pd.to_datetime(
        closed_times["date"].astype(str),
        format="%Y-%m-%d",
    )

    # TODO @marksp: Description doesn't exist in data from live dos, we should decide a default value
    closed_times["description"] = "From Live"

    notAvailable = (
        closed_times.groupby(["serviceid"])[["unavailableDate", "description"]]
        .apply(
            lambda x: [
                {
                    "unavailableDate": x["unavailableDate"]
                    .iloc[0]
                    .strftime("%Y-%m-%dT%H:%M:%S")
                    .strip(),
                    "description": x["description"].iloc[0],
                }
            ]
        )
        .reset_index(name="notAvailable")
    )

    return notAvailable
