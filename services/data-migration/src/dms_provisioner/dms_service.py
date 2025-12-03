from pathlib import Path

import chevron
from ftrs_common.logger import Logger
from sqlalchemy import Engine, text

LOGGER = Logger.get(service="DMS-Lambda-handler")
TEMPLATE_DIR = Path(__file__).parent / "templates"
RELATED_TABLES = ["serviceendpoints"]


def create_dms_user(engine: Engine, rds_username: str, rds_password: str) -> None:
    """
    Create DMS user in the target RDS instance
    """
    dms_user_template = (TEMPLATE_DIR / "create_dms_user.mustache").read_text()

    command = chevron.render(
        dms_user_template,
        {"rds_username": rds_username, "rds_password": rds_password},
    )

    with engine.connect() as conn:
        conn.execute(text(command))
        conn.commit()

    LOGGER.info("DMS user created")


def create_services_trigger(
    engine: Engine,
    lambda_arn: str,
    aws_region: str,
) -> None:
    """
    Create RDS trigger for services table to invoke Lambda on data changes
    """
    dms_template = (TEMPLATE_DIR / "services_trigger.mustache").read_text()
    command = chevron.render(
        dms_template,
        {
            "table_name": "services",
            "lambda_arn": lambda_arn,
            "aws_region": aws_region,
        },
    )
    with engine.connect() as connection:
        connection.execute(text(command))
        connection.commit()

    LOGGER.info("DB trigger for services table created successfully.")


def create_service_related_table_trigger(
    engine: Engine,
    lambda_arn: str,
    aws_region: str,
    table_name: str,
) -> None:
    """
    Create RDS trigger for related service tables to invoke Lambda on data changes
    """
    dms_template = (TEMPLATE_DIR / "service_related_trigger.mustache").read_text()
    command = chevron.render(
        dms_template,
        {
            "table_name": table_name,
            "lambda_arn": lambda_arn,
            "aws_region": aws_region,
        },
    )
    with engine.connect() as connection:
        connection.execute(text(command))
        connection.commit()

    LOGGER.info(f"DB trigger for {table_name} table created successfully.")


def create_rds_triggers(
    engine: Engine,
    lambda_arn: str,
    aws_region: str,
) -> None:
    """
    Create RDS trigger for replica database to invoke Lambda on data changes
    """
    create_services_trigger(
        engine=engine,
        lambda_arn=lambda_arn,
        aws_region=aws_region,
    )

    for table in RELATED_TABLES:
        create_service_related_table_trigger(
            engine=engine,
            lambda_arn=lambda_arn,
            aws_region=aws_region,
            table_name=table,
        )
