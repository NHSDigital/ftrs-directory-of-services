import json
import os
from dataclasses import dataclass

import pytest
from aws_lambda_powertools.event_handler import Response

from functions.logging.dos_logger import DosLogger
from tests.unit.functions.logging.setup_dummy_lambda import lambda_handler


@dataclass
class LambdaContext:
    function_name: str = "test"
    memory_limit_in_mb: int = 128
    invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
    aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"


@pytest.fixture
def lambda_context() -> LambdaContext:
    return LambdaContext()


@pytest.fixture
def create_assert_mandatory_fields_present(log_data):
    def assert_mandatory_fields_present(current_keys) -> None:
        for key in log_data.keys():
            assert key in current_keys, f"Missing mandatory log field: {key}"

    return assert_mandatory_fields_present


service = "test_logger"


@pytest.fixture
def dos_logger():
    return DosLogger.get(service=service)


class TestDosLogger:
    def test_extract(self, dos_logger, event, log_data):
        # Arrange
        extract = dict(log_data)
        # Act
        result = dos_logger.extract(event)
        # Assert
        assert result == extract

    def test_extract_one_time(self, dos_logger, event, details):
        # Arrange
        os.environ["ENVIRONMENT"] = "Development"
        os.environ["AWS_LAMBDA_FUNCTION_VERSION"] = "0.0.1"

        # Act
        result = dos_logger.extract_one_time(event)

        # Assert
        assert result == details

    def test_keys_clear_across_runs(self, caplog, ods_code, dos_logger, lambda_context):
        # Arrange
        def create_call_handler(message) -> Response:
            def call_handler() -> Response:
                dos_logger.info(message)
                capture = dos_logger.get_keys()
                return {
                    "capture": capture,
                    "response": Response(
                        status_code=123,
                        content_type="application/fhir+json",
                        body=json.dumps(dict()),
                    ),
                }

            return call_handler

        # Arrange - First run
        first_event = {
            "headers": {
                # Mandatory log field headers
                "NHSD-Correlation-ID": "correlation_id",
                "NHSD-Request-ID": "request_id",
                "Message-Id": "message_id",
                # One-time log field headers
                "NHSD-Api-Version": "v0.0.0",
                "NHSD-End-User-Role": "Clinician",
                "NHSD-Client-Id": "client_id",
                "NHSD-Connecting-Party-App-Name": "111-online",
            },
            "path": "/Organization",
            "httpMethod": "GET",
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|123",
                "_revinclude": "Endpoint:organization",
            },
            "requestContext": {
                "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
            },
            "body": None,
        }
        first_run_message = "test_1"
        first_run_handler = create_call_handler(first_run_message)

        # Act - First run
        response = lambda_handler(first_event, lambda_context, first_run_handler)
        first_capture = json.loads(
            json.dumps(response["capture"])
        )  # deep copy of capture dict due to mutability later in test case
        print("easy search", first_capture)

        # Arrange - Second run
        second_event = {
            "headers": {
                # Mandatory log field headers
                "NHSD-Correlation-ID": "correlation_id_2",
                "NHSD-Request-ID": "request_id",
                "Message-Id": "message_id",
                # One-time log field headers
                "NHSD-Api-Version": "v0.0.0",
                "NHSD-End-User-Role": "Clinician",
                "NHSD-Client-Id": "client_id",
                "NHSD-Connecting-Party-App-Name": "111-online",
            },
            "path": "/Organization",
            "httpMethod": "GET",
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|123",
                "_revinclude": "Endpoint:organization",
            },
            "requestContext": {
                "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
            },
            "body": None,
        }
        second_run_message = "test_2"
        second_run_handler = create_call_handler(second_run_message)

        # caplog_var = caplog.records
        # print("test search", caplog_var, "type", type(caplog_var))

        # Act - Second run
        intermediate_capture = json.loads(json.dumps(dos_logger.get_keys()))
        print("test search", intermediate_capture)
        response = lambda_handler(second_event, lambda_context, second_run_handler)
        second_capture = response["capture"]

        # Assert
        print("test search", first_capture)
        assert first_capture.get("dos_nhsd_correlation_id") == "correlation_id"
        # assert intermediate_capture == dict({"foo": "bar"})  # from first run
        assert second_capture.get("dos_nhsd_correlation_id") == "correlation_id_2"
        assert first_capture != second_capture

    def test_info_call(
        self,
        caplog,
        event,
        dos_logger,
        lambda_context,
        create_assert_mandatory_fields_present,
    ):
        # Arrange
        info_message = "test_info_call: testing info call"

        def call_info() -> Response:
            dos_logger.info(info_message)
            return Response(
                status_code=123,
                content_type="application/fhir+json",
                body=json.dumps(dict()),
            )

        # Act
        lambda_handler(event, lambda_context, call_info)
        capture = dos_logger.get_keys()

        # Assert
        create_assert_mandatory_fields_present(capture)
        assert "test_info_call: testing info call" in caplog.messages

    def test_warning_call(
        self,
        caplog,
        event,
        dos_logger,
        lambda_context,
        create_assert_mandatory_fields_present,
    ):
        # Arrange
        warning_message = "test_warning_call: testing warning call"

        def call_warning() -> Response:
            dos_logger.warning(warning_message)
            return Response(
                status_code=123,
                content_type="application/fhir+json",
                body=json.dumps(dict()),
            )

        # Act
        lambda_handler(event, lambda_context, call_warning)
        capture = dos_logger.get_keys()

        # Assert
        create_assert_mandatory_fields_present(capture)
        assert "test_warning_call: testing warning call" in caplog.messages

    def test_error_call(
        self,
        caplog,
        event,
        dos_logger,
        lambda_context,
        create_assert_mandatory_fields_present,
    ):
        # Arrange
        error_message = "test_error_call: testing error call"

        def call_error() -> Response:
            dos_logger.error(error_message)
            return Response(
                status_code=123,
                content_type="application/fhir+json",
                body=json.dumps(dict()),
            )

        # Act
        lambda_handler(event, lambda_context, call_error)
        capture = dos_logger.get_keys()

        # Assert
        create_assert_mandatory_fields_present(capture)
        assert "test_error_call: testing error call" in caplog.messages

    def test_exception_call(
        self,
        caplog,
        event,
        dos_logger,
        lambda_context,
        create_assert_mandatory_fields_present,
    ):
        # Arrange
        exception_message = "test_exception_call: testing exception call"

        def call_exception() -> Response:
            dos_logger.exception(exception_message)
            return Response(
                status_code=123,
                content_type="application/fhir+json",
                body=json.dumps(dict()),
            )

        # Act
        lambda_handler(event, lambda_context, call_exception)
        capture = dos_logger.get_keys()

        # Assert
        create_assert_mandatory_fields_present(capture)
        assert "test_exception_call: testing exception call" in caplog.messages
