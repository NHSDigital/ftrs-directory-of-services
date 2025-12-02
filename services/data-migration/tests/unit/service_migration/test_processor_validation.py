import unittest
from unittest.mock import MagicMock, patch

from ftrs_data_layer.domain import legacy

from service_migration.processor import DataMigrationProcessor
from service_migration.validation.types import ValidationIssue, ValidationResult


class TestDataMigrationProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.config = MagicMock()
        # Ensure the processor receives a valid connection string so create_engine succeeds
        self.config.db_config = MagicMock()
        self.config.db_config.connection_string = "sqlite+pysqlite:///:memory:"

        self.logger = MagicMock()
        self.processor = DataMigrationProcessor(config=self.config, logger=self.logger)
        self.processor.engine = MagicMock()
        self.processor.metadata = MagicMock()

        # Mock service and transformer
        self.service = MagicMock(spec=legacy.Service)
        self.service.id = 12345
        self.transformer = MagicMock()

        # Patch the get_transformer method to return our mock transformer
        self.get_transformer_patch = patch.object(
            self.processor, "get_transformer", return_value=self.transformer
        )
        self.mock_get_transformer = self.get_transformer_patch.start()

        # Mock _save method
        self.save_patch = patch.object(self.processor, "_save")
        self.mock_save = self.save_patch.start()

    def tearDown(self) -> None:
        self.get_transformer_patch.stop()
        self.save_patch.stop()

    def test_validation_process_valid(self) -> None:
        # Set up the transformer mock to return a valid validation result
        self.transformer.should_include_service.return_value = (True, "")
        validation_result = ValidationResult(
            origin_record_id=self.service.id, issues=[], sanitised=self.service
        )
        self.transformer.validator.validate.return_value = validation_result
        self.transformer.transform.return_value = MagicMock()

        # Call the process method
        self.processor._process_service(self.service)

        # Assert validation was called
        self.transformer.validator.validate.assert_called_once_with(self.service)

        # Assert metrics were updated correctly
        self.assertEqual(self.processor.metrics.total_records, 1)
        self.assertEqual(self.processor.metrics.supported_records, 1)
        self.assertEqual(self.processor.metrics.transformed_records, 1)
        self.assertEqual(self.processor.metrics.migrated_records, 1)
        self.assertEqual(self.processor.metrics.invalid_records, 0)

    def test_validation_process_invalid_but_continue(self) -> None:
        # Set up the transformer mock to return an invalid validation result that should continue
        self.transformer.should_include_service.return_value = (True, "")
        validation_issues = [
            ValidationIssue(
                expression=["field.name"],  # must be a list[str]
                severity="warning",  # required; warning => continue
                code="invalid",
                diagnostics="Invalid value",
                value="test",
            )
        ]
        validation_result = ValidationResult(
            origin_record_id=self.service.id,
            issues=validation_issues,
            sanitised=self.service,
        )
        self.transformer.validator.validate.return_value = validation_result
        self.transformer.transform.return_value = MagicMock()

        # Call the process method
        self.processor._process_service(self.service)

        # Assert validation was called
        self.transformer.validator.validate.assert_called_once_with(self.service)

        # Assert the transform method was called
        self.transformer.transform.assert_called_once()
        self.mock_save.assert_called_once()

        # Assert metrics were updated correctly
        self.assertEqual(
            self.processor.metrics.invalid_records, 0
        )  # Should not increment as should_continue=True
        self.assertEqual(self.processor.metrics.transformed_records, 1)

    def test_validation_process_invalid_and_stop(self) -> None:
        # Set up the transformer mock to return an invalid validation result that should not continue
        self.transformer.should_include_service.return_value = (True, "")
        validation_issues = [
            ValidationIssue(
                expression=["field.name"],  # must be a list[str]
                severity="fatal",  # required; fatal => do not continue
                code="critical",
                diagnostics="Critical error",
                value="test",
            )
        ]
        validation_result = ValidationResult(
            origin_record_id=self.service.id,
            issues=validation_issues,
            sanitised=self.service,
        )
        self.transformer.validator.validate.return_value = validation_result

        # Call the process method
        self.processor._process_service(self.service)

        # Assert validation was called
        self.transformer.validator.validate.assert_called_once_with(self.service)

        # Assert the transform method was not called
        self.transformer.transform.assert_not_called()

        # Assert metrics were updated correctly
        self.assertEqual(self.processor.metrics.invalid_records, 1)
        self.assertEqual(self.processor.metrics.transformed_records, 0)

    def test_convert_validation_issues_single_issue(self) -> None:
        issues = [
            ValidationIssue(
                value="test_value",
                severity="error",
                code="TEST_CODE",
                diagnostics="Test diagnostics",
                expression=["field_name"],
            )
        ]
        expected_result = [
            "field:['field_name'] ,error: TEST_CODE,message:Test diagnostics,value:test_value"
        ]
        result = self.processor._convert_validation_issues(issues)
        assert expected_result == result

    def test_convert_validation_issues_multiple_issues(self) -> None:
        issues = [
            ValidationIssue(
                value="value1",
                severity="error",
                code="CODE1",
                diagnostics="Diagnostics 1",
                expression=["field1"],
            ),
            ValidationIssue(
                value="value2",
                severity="warning",
                code="CODE2",
                diagnostics="Diagnostics 2",
                expression=["field2"],
            ),
        ]
        expected_result = [
            "field:['field1'] ,error: CODE1,message:Diagnostics 1,value:value1",
            "field:['field2'] ,error: CODE2,message:Diagnostics 2,value:value2",
        ]
        result = self.processor._convert_validation_issues(issues)
        assert expected_result == result

    def test_convert_validation_issues_empty_list(self) -> None:
        issues = []
        expected_result = []
        result = self.processor._convert_validation_issues(issues)
        assert expected_result == result
