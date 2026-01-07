from logging import ERROR, INFO

from ftrs_common.logbase import LogBase, LogReference
from ftrs_common.logger import Logger

LOGGER = Logger.get(service="ftrs-aws-local")


class ResetLogBase(LogBase):
    ETL_RESET_001 = LogReference(level=INFO, message="Initializing tables...")
    ETL_RESET_002 = LogReference(
        level=ERROR,
        message="The init option is only supported for the local environment.",
    )
    ETL_RESET_003 = LogReference(
        level=INFO, message="Table {table_name} created successfully."
    )
    ETL_RESET_004 = LogReference(
        level=INFO, message="Table {table_name} already exists."
    )
    ETL_RESET_005 = LogReference(
        level=ERROR,
        message="Invalid environment: {env}. Only 'dev' and 'local' are allowed.",
    )
    ETL_RESET_006 = LogReference(
        level=INFO, message="Deleted {count} items from {table_name}"
    )
