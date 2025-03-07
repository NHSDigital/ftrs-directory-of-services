import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

QUERY_GP_PRACTICE = """
SELECT "services"."name", "servicetypes"."name" AS "type", "services"."odscode", "services"."uid", "services"."id" AS "serviceid"
FROM "pathwaysdos"."services"
LEFT JOIN "pathwaysdos"."servicestatuses" ON "services"."statusid" = "servicestatuses"."id"
LEFT JOIN "pathwaysdos"."servicetypes" ON "services"."typeid" = "servicetypes"."id"
WHERE
    "servicestatuses"."name" = 'active' AND "services"."typeid" = '100' AND
    "services"."odscode" ~ '^[A-Za-z][0-9]{5}$';
"""

QUERY_GP_ENDPOINTS = """
WITH gp_practice AS (
    SELECT
        "services"."uid",
        "services"."name" AS "name",
        "servicetypes"."name" AS "type",
        "services"."odscode" AS "odscode",
        "services"."id" AS "serviceid"
    FROM "pathwaysdos"."services"
    LEFT JOIN "pathwaysdos"."servicetypes" ON "services"."typeid" = "servicetypes"."id"
    LEFT JOIN "pathwaysdos"."servicestatuses" ON "services"."statusid" = "servicestatuses"."id"
    WHERE
        "servicestatuses"."name" = 'active'
        AND "services"."typeid" = '100'
        AND "services"."odscode" ~ '^[A-Za-z][0-9]{5}$'
)
SELECT
    "serviceendpoints".*
FROM "gp_practice"
LEFT JOIN "pathwaysdos"."serviceendpoints" ON "gp_practice"."serviceid" = "serviceendpoints"."serviceid"
"""

QUERY_SERVICES_SIZE = """
SELECT COUNT(*) FROM "pathwaysdos"."services";
"""

QUERY_SERVICES_COLUMNS = """
SELECT COUNT(*)
FROM information_schema.columns
WHERE table_schema = 'pathwaysdos'
AND table_name = 'services';
"""

QUERY_SERVICEENDPOINTS_COLUMNS = """
SELECT COUNT(*)
FROM information_schema.columns
WHERE table_schema = 'pathwaysdos'
AND table_name = 'serviceendpoints';
"""


def get_gp_practices(db_uri: str) -> pd.DataFrame:
    return pd.read_sql(QUERY_GP_PRACTICE, db_uri)


def get_gp_endpoints(db_uri: str) -> pd.DataFrame:
    return pd.read_sql(QUERY_GP_ENDPOINTS, db_uri)


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


def logging_metrics(gp_practice_extract: pd.DataFrame, db_uri: str) -> None:
    # % of service profiles
    query_services_size = """
    SELECT COUNT(*) FROM "pathwaysdos"."services";
    """
    services_size = pd.read_sql(query_services_size, db_uri)["count"][0]
    gp_practice_extract_size = len(gp_practice_extract)
    logging.info(
        f"Percentage of service profiles: {gp_practice_extract_size / services_size * 100}%"
    )
    # % of all data fields
    services_columns = pd.read_sql(QUERY_SERVICES_COLUMNS, db_uri)["count"][0]
    serviceendpoints_columns = pd.read_sql(QUERY_SERVICEENDPOINTS_COLUMNS, db_uri)[
        "count"
    ][0]
    gp_practice_extract_column = gp_practice_extract.shape[1]
    logging.info(
        f"Percentage of all data fields: {gp_practice_extract_column / (services_columns + serviceendpoints_columns) * 100}%"
    )


def extract_gp_practice(db_uri: str, output_path: Path, clone_timestamp: str) -> None:
    gp_practice_df = get_gp_practices(db_uri)
    gp_practice_endpoints_df = get_gp_endpoints(db_uri)

    grouped_endpoints = format_endpoints(gp_practice_endpoints_df)

    gp_practice_extract = gp_practice_df.merge(
        grouped_endpoints, on="serviceid", how="left"
    ).drop(columns=["serviceid"])
    gp_practice_extract.to_parquet(
        output_path / f"dos-gp-practice-extract-{clone_timestamp}.parquet",
        engine="pyarrow",
        index=False,
        compression="zstd",
    )

    logging_metrics(gp_practice_extract, db_uri)


def extract(db_uri: str, output_path: Path) -> None:
    logging.info(f"Extracting data to {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    clone_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    extract_gp_practice(db_uri, output_path, clone_timestamp)


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
        required=True,
        help="Path to save the extracted data",
    )
    args = parser.parse_args(args)
    extract(args.db_uri, args.output_path)
