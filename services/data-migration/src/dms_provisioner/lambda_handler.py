import boto3
from ftrs_common.logger import Logger

from common.sql_utils import get_sqlalchemy_engine_from_config
from dms_provisioner.config import DmsDatabaseConfig
from dms_provisioner.dms_service import (
    create_dms_user,
    create_indexes_for_tables,
    create_rds_triggers,
    get_indexes_for_tables,
)

LOGGER = Logger.get(service="DMS-Lambda-handler")


@LOGGER.inject_lambda_context
def lambda_handler(event: dict, context: dict) -> None:
    LOGGER.info("Starting DMS provisioning process.")

    # Execute PostgreSQL trigger
    aws_region = boto3.session.Session().region_name

    # Use the optimized DatabaseConfig object
    dms_config = DmsDatabaseConfig()
    target_db_config = dms_config.get_target_rds_config()
    source_db_config = dms_config.get_source_db_config()
    rds_username, rds_password = dms_config.get_dms_user_details()

    # Connect to the RDS instance using the optimized engine creation
    engine = get_sqlalchemy_engine_from_config(target_db_config)

    # Create a user if not exists
    create_dms_user(engine, rds_username, rds_password)

    source_rds_engine = get_sqlalchemy_engine_from_config(source_db_config)

    create_indexes_for_tables(
        engine,
        get_indexes_for_tables(source_rds_engine, dms_config.schema_name),
        dms_config.schema_name,
    )

    # Create triggers for services and related tables
    create_rds_triggers(
        engine,
        lambda_arn=dms_config.trigger_lambda_arn,
        aws_region=aws_region,
    )

    LOGGER.info("DMS provisioning completed successfully.")
