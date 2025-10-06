import boto3
from botocore.exceptions import ClientError
from ftrs_common.logger import Logger

from pipeline.service.dms_service import create_dms_user, create_rds_trigger_replica_db
from pipeline.utils.config import DmsDatabaseConfig
from pipeline.utils.dbutil import get_sqlalchemy_engine_from_config

LOGGER = Logger.get(service="DMS-Lambda-handler")


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

        # create a user if not exists
        create_dms_user(engine, rds_username, rds_password)

        create_rds_trigger_replica_db(
            engine, rds_username, dms_config.trigger_lambda_arn, aws_region
        )

    except ClientError:
        LOGGER.exception("Error fetching secret for target RDS details or DMS user")
    except Exception:
        LOGGER.exception("Error something went wrong in the lambda handler")
    finally:
        if "engine" in locals():
            engine.dispose()
