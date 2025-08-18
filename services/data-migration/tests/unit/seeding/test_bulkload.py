import json
from typing import Generator
from unittest.mock import MagicMock

import pandas as pd
import pytest
from botocore.exceptions import ClientError
from pytest_mock import MockerFixture

from pipeline.seeding.bulkload import iter_batches, run_s3_restore, write_item_batch


@pytest.fixture(autouse=True)
def mock_console(mocker: MockerFixture) -> Generator[MagicMock, None, None]:
    yield mocker.patch("pipeline.seeding.bulkload.CONSOLE")


def test_iter_batches() -> None:
    """
    Test that iter_batches returns items in batches.
    """
    items = [json.dumps({"Item": {"id": i}}) for i in range(100)]

    expected_batch_size = 25
    expected_batch_count = 4

    batches = list(iter_batches(items))
    assert len(batches) == expected_batch_count
    assert all(len(batch) == expected_batch_size for batch in batches[:-1])
    assert len(batches[-1]) == expected_batch_size
    assert batches[0][0] == {"id": 0}


def test_write_item_batch(mocker: MockerFixture) -> None:
    ddb_mock = mocker.patch("pipeline.seeding.bulkload.DDB_CLIENT")
    ddb_mock.transact_write_items.return_value = None

    items = [{"id": i} for i in range(5)]

    write_item_batch("test_table", items)

    ddb_mock.transact_write_items.assert_called_once_with(
        TransactItems=[
            {"Put": {"TableName": "test_table", "Item": {"id": 0}}},
            {"Put": {"TableName": "test_table", "Item": {"id": 1}}},
            {"Put": {"TableName": "test_table", "Item": {"id": 2}}},
            {"Put": {"TableName": "test_table", "Item": {"id": 3}}},
            {"Put": {"TableName": "test_table", "Item": {"id": 4}}},
        ]
    )


def test_write_item_batch_backoff(
    mocker: MockerFixture,
    mock_console: MagicMock,
) -> None:
    ddb_mock = mocker.patch("pipeline.seeding.bulkload.DDB_CLIENT")
    sleep_mock = mocker.patch("pipeline.seeding.bulkload.sleep")

    ddb_mock.transact_write_items.side_effect = [
        ClientError({"Error": {"Code": "ThrottlingException"}}, "TransactWriteItems"),
        ClientError({"Error": {"Code": "ThrottlingException"}}, "TransactWriteItems"),
        None,
    ]

    batch = [{"id": i} for i in range(5)]
    write_item_batch("test_table", batch)

    expected_ddb_call_count = 3
    expected_sleep_call_count = 2

    assert ddb_mock.transact_write_items.call_count == expected_ddb_call_count
    assert sleep_mock.call_count == expected_sleep_call_count

    mock_console.print.assert_any_call(
        "Table test_table is being throttled. Waiting for 1 seconds...",
        style="yellow",
    )


def test_write_item_batch_clienterror(
    mocker: MockerFixture,
    mock_console: MagicMock,
) -> None:
    ddb_mock = mocker.patch("pipeline.seeding.bulkload.DDB_CLIENT")
    ddb_mock.transact_write_items.side_effect = ClientError(
        {"Error": {"Code": "SomeOtherError"}}, "TransactWriteItems"
    )

    batch = [{"id": i} for i in range(5)]

    write_item_batch("test_table", batch)

    mock_console.print.assert_any_call(
        "Error writing items to [bright_blue]test_table[/bright_blue]: An error occurred (SomeOtherError) when calling the TransactWriteItems operation: Unknown",
        style="bright_red",
    )


def test_write_item_batch_exception(
    mocker: MockerFixture,
    mock_console: MagicMock,
) -> None:
    ddb_mock = mocker.patch("pipeline.seeding.bulkload.DDB_CLIENT")
    ddb_mock.transact_write_items.side_effect = Exception("Some error message")

    batch = [{"id": i} for i in range(5)]

    write_item_batch("test_table", batch)

    mock_console.print.assert_any_call(
        "Error writing items to [bright_blue]test_table[/bright_blue]: Some error message",
        style="bright_red",
    )


@pytest.mark.asyncio
async def test_run_s3_restore(mocker: MockerFixture) -> None:
    mock_get_parameter = mocker.patch(
        "pipeline.seeding.bulkload.get_parameter",
        return_value={
            "healthcare-service": "s3://test-store/healthcare-service.parquet",
            "organisation": "s3://test-store/organisation.parquet",
            "location": "s3://test-store/location.parquet",
        },
    )

    mock_read_parquet = mocker.patch(
        "pipeline.seeding.bulkload.wr.s3.read_parquet",
        side_effect=[
            pd.DataFrame(data=[["healthcare-service"]], columns=["data"]),
            pd.DataFrame(data=[["organisation"]], columns=["data"]),
            pd.DataFrame(data=[["location"]], columns=["data"]),
        ],
    )

    mock_bulk_load_table = mocker.patch(
        "pipeline.seeding.bulkload.bulk_load_table",
        return_value=None,
    )

    await run_s3_restore("local", "fdos-000")

    mock_read_parquet.assert_has_calls(
        [
            mocker.call(path="s3://test-store/healthcare-service.parquet"),
            mocker.call(path="s3://test-store/organisation.parquet"),
            mocker.call(path="s3://test-store/location.parquet"),
        ]
    )

    mock_bulk_load_table.assert_has_calls(
        [
            mocker.call(
                "ftrs-dos-local-database-healthcare-service-fdos-000",
                ["healthcare-service"],
            ),
            mocker.call(
                "ftrs-dos-local-database-organisation-fdos-000",
                ["organisation"],
            ),
            mocker.call(
                "ftrs-dos-local-database-location-fdos-000",
                ["location"],
            ),
        ]
    )

    mock_get_parameter.assert_called_once_with(
        name="/ftrs-dos/local/dynamodb-backup-arns", transform="json"
    )
