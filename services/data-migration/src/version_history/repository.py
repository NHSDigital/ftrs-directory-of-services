"""Repository for version history records."""

from botocore.exceptions import ClientError
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_table_name
from ftrs_data_layer.client import get_dynamodb_resource

from version_history.models import VersionHistoryRecord

logger = Logger.get(service="version-history-repository")


class VersionHistoryRepository:
    """Repository for managing version history records in DynamoDB."""

    def __init__(self, endpoint_url: str | None = None) -> None:
        """
        Initialize the repository.

        Args:
            endpoint_url: Optional DynamoDB endpoint URL (for local development)
        """
        self.dynamodb = get_dynamodb_resource(endpoint_url)
        self.table_name = get_table_name("version-history")
        self.table = self.dynamodb.Table(self.table_name)
        logger.log("VH_REPO_001", table_name=self.table_name)

    def write_change_record(self, record: VersionHistoryRecord) -> None:
        """
        Write a version history record to DynamoDB.

        Args:
            record: The version history record to write

        Raises:
            ClientError: If the DynamoDB write operation fails
        """
        try:
            item = record.to_dynamodb_item()
            logger.log(
                "VH_REPO_002",
                entity_id=record.entity_id,
                timestamp=record.timestamp,
                change_type=record.change_type,
            )

            self.table.put_item(Item=item)

            logger.log(
                "VH_REPO_003",
                entity_id=record.entity_id,
            )

        except ClientError as e:
            logger.error(
                f"Failed to write version history record for {record.entity_id}: {e}",
                exc_info=True,
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error writing version history record for {record.entity_id}: {e}",
                exc_info=True,
            )
            raise
