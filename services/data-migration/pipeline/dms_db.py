from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from ftrs_common.logger import Logger
from ftrs_data_layer.domain import legacy
from pydantic import SecretStr
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from pipeline.utils.config import DatabaseConfig, DmsDatabaseConfig

LOGGER = Logger.get(service="DMS-DB-Trigger")


# Initialize config and fetch environment variables
target_rds_details, dms_user_details, trigger_lambda_arn = (
    DmsDatabaseConfig().get_values()
)


def get_sqlalchemy_engine_from_config(db_config: DatabaseConfig) -> Engine:
    """Create and configure an SQLAlchemy engine from DatabaseConfig with optimized settings."""
    return create_engine(
        db_config.connection_string,
        # Connection pool settings for better performance
        pool_size=10,  # Number of connections to maintain in a pool
        max_overflow=20,  # Additional connections beyond pool_size
        pool_pre_ping=True,  # Validate connections before use
        pool_recycle=3600,  # Recycle connections after 1 hour
        # Connection timeout settings
        connect_args={
            "connect_timeout": 30,  # Connection timeout in seconds
            "application_name": "dms_pipeline",  # Identify your application in pg_stat_activity
        },
        # Enable connection pooling optimizations
        pool_reset_on_return="commit",  # Reset connections on return to pool
    )


def get_sqlalchemy_engine(
    host: str, db: str, user: str, password: str, port: int
) -> Engine:
    """Create and configure an SQLAlchemy engine for PostgreSQL with optimized settings."""
    # Create a DatabaseConfig instance and use the optimized function
    db_config = DatabaseConfig(
        host=host, port=port, username=user, password=SecretStr(password), dbname=db
    )
    return get_sqlalchemy_engine_from_config(db_config)


def execute_rds_command(engine: Engine, rds_username: str, rds_password: str) -> None:
    try:
        # Create a SQL command with a password placeholder
        command = f"""DO $$ BEGIN
                IF NOT EXISTS (
                SELECT FROM pg_catalog.pg_roles WHERE rolname = '{rds_username}'
                ) THEN
                CREATE ROLE {rds_username} LOGIN PASSWORD '{rds_password}';
                GRANT rds_replication TO {rds_username};
                GRANT SELECT ON ALL TABLES IN SCHEMA public TO {rds_username};
                END IF;
                END $$;"""

        # Using a parameterized query to avoid password in logs
        with engine.connect() as connection:
            # Execute the command with parameters
            connection.execute(text(command), {"password": rds_password})
            connection.commit()
        LOGGER.log("RDS command executed successfully.")
    except Exception:
        LOGGER.exception("Failed to execute RDS command")
        raise


def execute_postgresql_trigger(
    engine: Engine,
    rds_username: str,
    lambda_arn: str,
    aws_region: str,
) -> None:
    try:
        # Read the SQL template file
        template_path = Path(__file__).parent / "templates" / "trigger.sql.tmpl"
        with open(template_path, "r") as file:
            sql_template = file.read()

        # Replace placeholders with actual values
        sql_commands = sql_template.replace("${user}", rds_username)
        sql_commands = sql_commands.replace("${lambda_arn}", lambda_arn)
        sql_commands = sql_commands.replace("${aws_region}", aws_region)
        sql_commands = sql_commands.replace(
            "${table_name}", legacy.Services.__tablename__
        )

        # Execute the SQL commands as a single statement
        with engine.connect() as connection:
            connection.execute(text(sql_commands))
            connection.commit()

        LOGGER.info("PostgreSQL trigger executed successfully.")
    except Exception:
        LOGGER.exception("Failed to execute PostgreSQL trigger")
        raise


def lambda_handler(event: dict, context: dict) -> None:
    try:
        # Execute PostgreSQL trigger
        aws_region = boto3.session.Session().region_name

        # Use the optimized DatabaseConfig object
        dms_config = DmsDatabaseConfig()
        target_db_config = dms_config.get_target_rds_details()
        rds_username, rds_password = dms_config.get_dms_user_details()

        # Connect to the RDS instance using the optimized engine creation
        engine = get_sqlalchemy_engine_from_config(target_db_config)

        # Execute RDS command
        execute_rds_command(engine, rds_username, rds_password)

        execute_postgresql_trigger(engine, rds_username, trigger_lambda_arn, aws_region)

    except ClientError:
        LOGGER.exception("Error fetching secret for target RDS details or DMS user")
    except Exception:
        LOGGER.exception("Error something went wrong in the lambda handler")
    finally:
        if "engine" in locals():
            engine.dispose()
