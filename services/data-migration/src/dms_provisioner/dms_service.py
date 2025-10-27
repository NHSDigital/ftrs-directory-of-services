from pathlib import Path

from ftrs_common.logger import Logger
from ftrs_data_layer.domain import legacy
from sqlalchemy import Engine, text

LOGGER = Logger.get(service="DMS-Lambda-handler")


def create_dms_user(engine: Engine, rds_username: str, rds_password: str) -> None:
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
        LOGGER.info("DMS user created")
    except Exception:
        LOGGER.exception("Failed to execute RDS command")
        raise


def create_rds_trigger_replica_db(
    engine: Engine,
    rds_username: str,
    lambda_arn: str,
    aws_region: str,
) -> None:
    try:
        # Read the SQL template file
        template_path = Path(__file__).parent / "trigger.sql.tmpl"
        with open(template_path, "r") as file:
            sql_template = file.read()

        # Replace placeholders with actual values
        sql_commands = sql_template.replace("${user}", rds_username)
        sql_commands = sql_commands.replace("${lambda_arn}", lambda_arn)
        sql_commands = sql_commands.replace("${aws_region}", aws_region)
        sql_commands = sql_commands.replace(
            "${table_name}", "pathwaysdos." + legacy.Service.__tablename__
        )

        # Execute the SQL commands as a single statement
        with engine.connect() as connection:
            connection.execute(text(sql_commands))
            connection.commit()

        LOGGER.info("DB trigger created successfully.")
    except Exception:
        LOGGER.exception("Failed to create DB trigger for replica DB")
        raise
