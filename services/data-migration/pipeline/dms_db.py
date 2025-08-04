import logging
import os

import boto3
import pymysql
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

secrets_client = boto3.client("secretsmanager")


def fetch_environment_variables() -> tuple[str, str, int, str, str]:
    try:
        cluster_endpoint = os.environ["RDS_CLUSTER_ENDPOINT"]
        database_name = os.environ["RDS_DATABASE_NAME"]
        rds_port = int(os.environ["RDS_PORT"])
        secret_name = os.environ["SECRET_NAME"]
    except KeyError:
        logger.exception("Missing environment variable")
        raise
    else:
        return cluster_endpoint, database_name, rds_port, secret_name


# Fetch environment variables
cluster_endpoint, database_name, rds_port, secret_name = fetch_environment_variables()


def execute_rds_command(
    connection: pymysql.connections.Connection, rds_username: str, rds_password: str
) -> None:
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
        with connection.cursor() as cursor:
            cursor.execute(command)
            connection.commit()
        logger.info("RDS command executed successfully.")
    except Exception:
        logger.exception("Failed to execute RDS command")


def lambda_handler(event: dict, context: dict) -> None:
    try:
        # Fetch credentials from Secrets Manager
        secret_response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = eval(secret_response["SecretString"])
        username = secret["username"]
        password = secret["password"]
        rds_username = secret.get("rds_username")
        rds_password = secret.get("rds_password")

        # Connect to the RDS instance
        connection = pymysql.connect(
            host=cluster_endpoint,
            user=username,
            password=password,
            database=database_name,
            port=rds_port,
        )

        # Create a new user
        with connection.cursor() as cursor:
            new_user = event["new_user"]
            new_password = event["new_password"]
            cursor.execute(
                f"CREATE USER '{new_user}'@'%' IDENTIFIED BY '{new_password}';"
            )
            connection.commit()

        logger.info(f"Successfully created user: {new_user}")

        # Execute RDS command
        execute_rds_command(connection, rds_username, rds_password)

    except ClientError:
        logger.exception("Error fetching secret")
    except pymysql.MySQLError:
        logger.exception("Database error")
    except Exception:
        logger.exception("Unexpected error")
    finally:
        if "connection" in locals() and connection.open:
            connection.close()
            logger.info("Database connection closed.")
