import unittest
from unittest.mock import MagicMock, patch

from boto3.dynamodb.conditions import Key
from services.ftrs_service.repository.dynamo import (
    DynamoRepository,
    OrganizationRecord,
)


class TestDynamoRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.table_name = "test-table"
        self.mock_table = MagicMock()
        self.mock_dynamodb = MagicMock()
        self.mock_dynamodb.Table.return_value = self.mock_table

        self.boto3_resource_patcher = patch("boto3.resource")
        self.mock_boto3_resource = self.boto3_resource_patcher.start()
        self.mock_boto3_resource.return_value = self.mock_dynamodb

        self.repository = DynamoRepository(self.table_name)

    def tearDown(self) -> None:
        self.boto3_resource_patcher.stop()

    def test_init(self) -> None:
        self.mock_boto3_resource.assert_called_once_with("dynamodb")
        self.mock_dynamodb.Table.assert_called_once_with(self.table_name)
        self.assertEqual(self.repository.table, self.mock_table)

    def test_get_first_record_by_ods_code_found_single(self) -> None:
        ods_code = "ABC123"

        sample_item = {
            "id": "123",
            "ods-code": ods_code,
        }

        self.mock_table.query.return_value = {"Items": [sample_item], "Count": 1}

        mock_org_record = MagicMock(spec=OrganizationRecord)
        with patch(
            "services.ftrs_service.repository.dynamo.OrganizationRecord.from_dynamo_item",
            return_value=mock_org_record,
        ) as mock_from_dynamo:
            result = self.repository.get_first_record_by_ods_code(ods_code)

            self.mock_table.query.assert_called_once_with(
                IndexName="ods-code-index",
                KeyConditionExpression=Key("ods-code").eq(ods_code),
            )

            mock_from_dynamo.assert_called_once_with(sample_item)

            self.assertEqual(result, mock_org_record)

    def test_get_first_record_by_ods_code_found_multiple(self) -> None:
        ods_code = "ABC123"

        sample_items = [
            {
                "id": "123",
                "ods-code": ods_code,
            },
            {
                "id": "456",
                "ods-code": ods_code,
            },
        ]

        self.mock_table.query.return_value = {"Items": sample_items, "Count": 2}

        mock_org_record = MagicMock(spec=OrganizationRecord)
        with patch(
            "services.ftrs_service.repository.dynamo.OrganizationRecord.from_dynamo_item",
            return_value=mock_org_record,
        ) as mock_from_dynamo:
            result = self.repository.get_first_record_by_ods_code(ods_code)

            self.mock_table.query.assert_called_once_with(
                IndexName="ods-code-index",
                KeyConditionExpression=Key("ods-code").eq(ods_code),
            )

            mock_from_dynamo.assert_called_once_with(sample_items[0])

            self.assertEqual(result, mock_org_record)

    def test_get_first_record_by_ods_code_not_found(self):
        ods_code = "ABC123"

        self.mock_table.query.return_value = {"Items": [], "Count": 0}

        result = self.repository.get_first_record_by_ods_code(ods_code)

        self.mock_table.query.assert_called_once_with(
            IndexName="ods-code-index",
            KeyConditionExpression=Key("ods-code").eq(ods_code),
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
