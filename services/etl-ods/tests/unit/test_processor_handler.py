import json
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Generator

import pytest
import requests
from ftrs_common.utils.correlation_id import set_correlation_id
from ftrs_common.utils.request_id import set_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture

from producer.processor import processor
from producer.processor_handler import MAX_DAYS_PAST, processor_lambda_handler

TEST_CORRELATION_ID = "test-correlation"
TEST_REQUEST_ID = "test-request"


@pytest.fixture(autouse=True)
def fixed_ids() -> Generator[None, None, None]:
    set_correlation_id(TEST_CORRELATION_ID)
    set_request_id(TEST_REQUEST_ID)
    yield
    set_correlation_id(None)
    set_request_id(None)


def test_processor_lambda_handler_success(mocker: MockerFixture) -> None:
    mock_processor = mocker.patch("producer.processor_handler.processor")
    date = datetime.now().strftime("%Y-%m-%d")
    event = {"date": date}

    response = processor_lambda_handler(event, {})

    mock_processor.assert_called_once_with(date=date)
    assert response == {"statusCode": 200, "body": "Processing complete"}


def test_processor_lambda_handler_success_is_scheduled(
    mocker: MockerFixture,
) -> None:
    mock_processor = mocker.patch("producer.processor_handler.processor")

    event = {"is_scheduled": True}

    response = processor_lambda_handler(event, {})

    previous_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    mock_processor.assert_called_once_with(date=previous_date)
    assert response == {"statusCode": 200, "body": "Processing complete"}


def test_processor_lambda_handler_missing_date() -> None:
    response = processor_lambda_handler({}, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert json.loads(response["body"]) == {"error": "Date parameter is required"}


def test_processor_lambda_handler_invalid_date_format() -> None:
    invalid_event = {"date": "14-05-2025"}
    response = processor_lambda_handler(invalid_event, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert json.loads(response["body"]) == {
        "error": "Date must be in YYYY-MM-DD format"
    }


def test_processor_lambda_handler_date_too_old(mocker: MockerFixture) -> None:
    old_date = "2023-01-01"
    event = {"date": old_date}
    mock_processor = mocker.patch("producer.processor_handler.processor")
    response = processor_lambda_handler(event, {})

    mock_processor.assert_not_called()
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert json.loads(response["body"]) == {
        "error": f"Date must not be more than {MAX_DAYS_PAST} days in the past"
    }


def test_processor_lambda_handler_date_exactly_185_days(mocker: MockerFixture) -> None:
    date_185_days_ago = (datetime.now().date() - timedelta(days=185)).strftime(
        "%Y-%m-%d"
    )
    event = {"date": date_185_days_ago}
    mock_processor = mocker.patch("producer.processor_handler.processor")
    response = processor_lambda_handler(event, {})
    mock_processor.assert_called_once_with(date=date_185_days_ago)
    assert response == {"statusCode": 200, "body": "Processing complete"}


def test_processor_lambda_handler_exception(mocker: MockerFixture) -> None:
    mock_processor = mocker.patch("producer.processor_handler.processor")
    mock_processor.side_effect = Exception("Test error")
    date = datetime.now().strftime("%Y-%m-%d")
    event = {"date": date}

    result = processor_lambda_handler(event, {})

    mock_processor.assert_called_once_with(date=date)
    assert str(result["statusCode"]) == "500"
    error_body = json.loads(result["body"])
    assert "Unexpected error: Test error" in error_body["error"]


def test_processor_logs_and_raises_request_exception(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch(
        "producer.processor.fetch_outdated_organisations",
        side_effect=requests.exceptions.RequestException("network fail"),
    )
    date = datetime.now().strftime("%Y-%m-%d")
    with caplog.at_level("INFO"):
        with pytest.raises(requests.exceptions.RequestException, match="network fail"):
            processor(date)
        expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_022.value.message.format(
            error_message="network fail"
        )
        assert expected_log in caplog.text


def test_processor_logs_and_raises_generic_exception(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch(
        "producer.processor.fetch_outdated_organisations",
        side_effect=Exception("unexpected error"),
    )
    date = datetime.now().strftime("%Y-%m-%d")
    with caplog.at_level("INFO"):
        with pytest.raises(Exception, match="unexpected error"):
            processor(date)
        expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_023.value.message.format(
            error_message="unexpected error"
        )
        assert expected_log in caplog.text
