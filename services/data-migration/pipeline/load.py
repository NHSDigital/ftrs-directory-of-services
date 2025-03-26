import logging
from pathlib import Path

import pandas as pd

# TODO:Load the sanitised and filtered data into the new data store, correctly formatted:
# - Use the transformed service records and write a process to load those records into the database.
# - Implemented as a Python function that could be called via CLI or Lambda invocation
# - Can be reused for loading in pre-transformed sample test data if required (aka extract)


# TODO: can insert methods be refactored so more generic and resuable? e.g. passing in table_name
def insert_endpoints_to_db(
    endpoint_df: pd.DataFrame, db_uri: str, table_name: str
) -> None:
    #  make a generic upload
    endpoints = pd.DataFrame()
    # TODO: endpoints can be a list of dictionaries, so fix loop below
    # - so loop over the list and insert each dictionary as a row in the database
    # - handle empty lists
    for row in endpoint_df:
        dataframe_formatted = pd.DataFrame(row, index=[0])
        for key, value in row.items():
            dataframe_formatted[key] = value
        endpoints = pd.concat([endpoints, dataframe_formatted], ignore_index=True)
    # TODO: then load endpoints
    # try:
    #     dataframe_total.to_sql(table_name, db_uri, schema='Core', if_exists='replace', index=False, chunksize=1)
    #     logging.info("Endpoint data loaded successfully")
    # except Exception as e:
    #     logging.error(f"Error loading Endpoint data: {e}")


def insert_organisations_to_db(organisation_df: pd.DataFrame, db_uri: str) -> None:
    #  make an organisation df with the organisation rows in appropriate format
    organisations = pd.DataFrame()
    for row in organisation_df:
        # put the key value pairs into one dataframe, where each key is a column and all the values form one row
        dataframe = pd.DataFrame(row, index=[0])
        for key, value in row.items():
            dataframe[key] = value
        # Notes: loop to_sql for each row but this overwrites the table each time as index is 0 for all
        # - so group in one df, and add all, using chunksize for row by row approach
        organisations = pd.concat([organisations, dataframe], ignore_index=True)
    try:
        # TODO: consider chunksize amount for efficency?
        organisations.to_sql(
            "Organisation",
            db_uri,
            schema="Core",
            if_exists="replace",
            index=False,
            chunksize=1,
        )
        logging.info("Organisation data loaded successfully")
    except Exception as e:
        logging.error(f"Error loading Organisation data: {e}")


def load_gp_practices(db_uri: str, input_path: Path) -> None:
    # TODO: Load data from a parquet file to a database
    # - Read the Parquet file into a DataFrame
    # - Create SQL code to insert the data into the database
    # -- enter data for table Organisation
    # -- enter data for table Endpoint

    # gp df has organisation and endpoint data
    gp_practice_df = pd.read_parquet(input_path)

    organisation_df = gp_practice_df["organisation"]
    # Notes: use dataframe instead of series (not e.g. organisation_series = gp_practice_df.iloc[:, 0] )
    insert_organisations_to_db(organisation_df, db_uri)

    endpoint_df = gp_practice_df["endpoint"]
    insert_endpoints_to_db(endpoint_df, db_uri, "Endpoint")


def load(db_uri: str, input_path: Path) -> None:
    # Notes: in starget-state.sql, comment out foreign keys for tables not in use
    logging.info(f"Loading data from {input_path}")
    logging.info("Implementation in progress")
    load_gp_practices(db_uri, input_path)


def main(args: list[str] | None = None) -> None:
    import argparse

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(description="Load data to destination")
    parser.add_argument(
        "--input-path", type=Path, required=True, help="Path to load the extracted data"
    )
    parser.add_argument(
        "--db-uri", type=str, required=True, help="URI to connect to the database"
    )
    args = parser.parse_args(args)
    load(args.db_uri, args.input_path)
