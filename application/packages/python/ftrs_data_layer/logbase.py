from logging import DEBUG, ERROR, INFO, WARNING

from ftrs_common.logger import LogBase, LogReference


class DDBLogBase(LogBase):
    """
    LogBase for DynamoDB operations.
    """

    DDB_CORE_001 = LogReference(level=DEBUG, message="Initialised DynamoDB repository")
    DDB_CORE_002 = LogReference(level=DEBUG, message="Putting item into DynamoDB table")
    DDB_CORE_003 = LogReference(level=INFO, message="Item put into DynamoDB table")
    DDB_CORE_004 = LogReference(
        level=ERROR, message="Error putting item into DynamoDB table"
    )

    DDB_CORE_005 = LogReference(level=DEBUG, message="Getting item from DynamoDB table")
    DDB_CORE_006 = LogReference(
        level=INFO, message="Item retrieved from DynamoDB table"
    )
    DDB_CORE_007 = LogReference(
        level=ERROR, message="Error retrieving item from DynamoDB table"
    )
    DDB_CORE_008 = LogReference(
        level=WARNING, message="Item not found in DynamoDB table"
    )

    DDB_CORE_009 = LogReference(level=DEBUG, message="Querying DynamoDB table")
    DDB_CORE_010 = LogReference(level=INFO, message="Completed query on DynamoDB table")
    DDB_CORE_011 = LogReference(level=ERROR, message="Error querying DynamoDB table")

    DDB_CORE_012 = LogReference(
        level=DEBUG, message="Perfoming batch write to DynamoDB"
    )
    DDB_CORE_013 = LogReference(level=INFO, message="Completed batch write to DynamoDB")
    DDB_CORE_014 = LogReference(level=ERROR, message="Error performing batch write")
    DDB_CORE_015 = LogReference(level=ERROR, message="Unprocessed items in batch write")
