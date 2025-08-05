import logging
import os
import re

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

MIN_PASSWORD_LENGTH = 16

secrets_client = boto3.client("secretsmanager")


def fetch_environment_variables() -> tuple[str, str, str, str]:
    try:
        target_rds_details = os.environ["TARGET_RDS_DETAILS"]
        dms_user_details = os.environ["DMS_USER_DETAILS"]
        trigger_lambda_arn = os.environ["TRIGGER_LAMBDA_ARN"]
    except KeyError:
        logger.exception("Missing environment variable")
        raise
    else:
        return target_rds_details, dms_user_details, trigger_lambda_arn


# Fetch environment variables
target_rds_details, dms_user_details, trigger_lambda_arn = fetch_environment_variables()


def get_sqlalchemy_engine(
    host: str, db: str, user: str, password: str, port: int
) -> Engine:
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)


def execute_rds_command(engine: Engine, rds_username: str, rds_password: str) -> None:
    try:
        command = f"""DO $$ BEGIN
                IF NOT EXISTS (
                SELECT FROM pg_catalog.pg_roles WHERE rolname = '{rds_username}'
                ) THEN
                CREATE ROLE {rds_username} LOGIN PASSWORD '{rds_password}';
                GRANT rds_replication TO {rds_username};
                GRANT SELECT ON ALL TABLES IN SCHEMA public TO {rds_username};
                END IF;
                END $$;"""
        with engine.connect() as connection:
            connection.execute(text(command))
            connection.commit()
        logger.info("RDS command executed successfully.")
    except Exception:
        logger.exception("Failed to execute RDS command")
        raise


def execute_postgresql_trigger(
    engine: Engine,
    rds_username: str,
    lambda_arn: str,
    aws_region: str,
) -> None:
    try:
        # Read the SQL template file
        with open(
            "trigger.sql.tmpl",
            "r",
        ) as file:
            sql_template = file.read()

        table_name = "pathwaysdos.services"
        # Replace placeholders with actual values
        sql_commands = re.sub(r"\\$\\{user\\}", rds_username, sql_template)
        sql_commands = re.sub(r"\\$\\{lambda_arn\\}", lambda_arn, sql_commands)
        sql_commands = re.sub(r"\\$\\{aws_region\\}", aws_region, sql_commands)
        sql_commands = re.sub(r"\\$\\{table_name\\}", table_name, sql_commands)

        # Execute the SQL commands
        with engine.connect() as connection:
            for command in sql_commands.split(";"):
                if command.strip():
                    connection.execute(text(command))
            connection.commit()

        logger.info("PostgreSQL trigger executed successfully.")
    except Exception:
        logger.exception("Failed to execute PostgreSQL trigger")
        raise


def get_target_rds_details() -> tuple[str, str, int, str, str]:
    target_rds_details_response = secrets_client.get_secret_value(
        SecretId=target_rds_details
    )
    target_rds_details_secret = eval(target_rds_details_response["SecretString"])

    cluster_endpoint = target_rds_details_secret["host"]
    database_name = target_rds_details_secret["dbname"]
    port = target_rds_details_secret["port"]
    username = target_rds_details_secret["username"]
    password = target_rds_details_secret["password"]

    return cluster_endpoint, database_name, port, username, password


def get_dms_user_details() -> tuple[str, str]:
    dms_user_details_response = secrets_client.get_secret_value(
        SecretId=dms_user_details
    )
    rds_password = dms_user_details_response["SecretString"]
    rds_username = "dms_user"

    return rds_username, rds_password


def lambda_handler(event: dict, context: dict) -> None:
    try:
        cluster_endpoint, database_name, port, username, password = (
            get_target_rds_details()
        )

        rds_username, rds_password = get_dms_user_details()

        # Connect to the RDS instance using SQLAlchemy
        engine = get_sqlalchemy_engine(
            host=cluster_endpoint,
            db=database_name,
            user=username,
            password=password,
            port=port,
        )

        # Execute RDS command
        execute_rds_command(engine, rds_username, rds_password)

        # Execute PostgreSQL trigger
        aws_region = boto3.session.Session().region_name
        execute_postgresql_trigger(engine, rds_username, trigger_lambda_arn, aws_region)

    except ClientError:
        logger.exception("Error fetching secret")
    except Exception:
        logger.exception("Unexpected error")
    finally:
        if "engine" in locals():
            engine.dispose()
            logger.info("Database engine disposed.")
