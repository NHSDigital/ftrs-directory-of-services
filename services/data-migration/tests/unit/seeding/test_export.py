import gzip
import json
from io import BytesIO

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from pipeline.seeding.export import (
    decompress_and_parse_files,
    download_exported_files,
    export_table,
    get_export_file_list,
    get_s3_bucket_name,
    get_table_arn,
    is_export_complete,
    process_export,
    run_s3_export,
    trigger_table_export,
)


def test_get_s3_bucket_name() -> None:
    result = get_s3_bucket_name(env="dev")
    assert result == "ftrs-dos-dev-data-migration-pipeline-store"


def test_get_s3_bucket_name_workspace() -> None:
    result = get_s3_bucket_name(env="dev", workspace="test_workspace")
    assert result == "ftrs-dos-dev-data-migration-pipeline-store-test_workspace"


def test_get_table_arn(mocker: MockerFixture) -> None:
    mock_ddb_client = mocker.MagicMock()
    mock_ddb_client.describe_table.return_value = {
        "Table": {"TableArn": "arn:aws:dynamodb:region:account-id:table/test_table"}
    }

    mocker.patch(
        "pipeline.seeding.export.get_dynamodb_client",
        return_value=mock_ddb_client,
    )

    result = get_table_arn("test_table")

    assert result == "arn:aws:dynamodb:region:account-id:table/test_table"
    mock_ddb_client.describe_table.assert_called_once_with(TableName="test_table")


def test_trigger_table_export(mocker: MockerFixture) -> None:
    mock_ddb_client = mocker.MagicMock()
    mock_ddb_client.describe_table.return_value = {
        "Table": {"TableArn": "arn:aws:dynamodb:region:account-id:table/test_table"}
    }
    mock_ddb_client.export_table_to_point_in_time.return_value = {
        "ExportDescription": {
            "ExportArn": "arn:aws:dynamodb:region:account-id:table/test_table/export"
        }
    }

    mocker.patch(
        "pipeline.seeding.export.get_dynamodb_client", return_value=mock_ddb_client
    )

    result = trigger_table_export("test_table", "test_s3_bucket_name")

    assert result == {
        "ExportArn": "arn:aws:dynamodb:region:account-id:table/test_table/export"
    }
    mock_ddb_client.export_table_to_point_in_time.assert_called_once_with(
        TableArn="arn:aws:dynamodb:region:account-id:table/test_table",
        S3Bucket="test_s3_bucket_name",
        S3Prefix="exports/test_table/",
    )


def test_is_export_complete_in_progress(mocker: MockerFixture) -> None:
    mock_ddb_client = mocker.MagicMock()
    mock_ddb_client.describe_export.return_value = {
        "ExportDescription": {
            "ExportArn": "arn:aws:dynamodb:region:account-id:table/test_table/export",
            "ExportStatus": "IN_PROGRESS",
        }
    }

    mocker.patch(
        "pipeline.seeding.export.get_dynamodb_client", return_value=mock_ddb_client
    )

    result = is_export_complete(
        "arn:aws:dynamodb:region:account-id:table/test_table/export"
    )

    assert result is False
    mock_ddb_client.describe_export.assert_called_once_with(
        ExportArn="arn:aws:dynamodb:region:account-id:table/test_table/export"
    )


def test_is_export_complete_queued(mocker: MockerFixture) -> None:
    mock_ddb_client = mocker.MagicMock()
    mock_ddb_client.describe_export.return_value = {
        "ExportDescription": {
            "ExportArn": "arn:aws:dynamodb:region:account-id:table/test_table/export",
            "ExportStatus": "QUEUED",
        }
    }

    mocker.patch(
        "pipeline.seeding.export.get_dynamodb_client", return_value=mock_ddb_client
    )

    result = is_export_complete(
        "arn:aws:dynamodb:region:account-id:table/test_table/export"
    )

    assert result is False
    mock_ddb_client.describe_export.assert_called_once_with(
        ExportArn="arn:aws:dynamodb:region:account-id:table/test_table/export"
    )


def test_is_export_complete_completed(mocker: MockerFixture) -> None:
    mock_ddb_client = mocker.MagicMock()
    mock_ddb_client.describe_export.return_value = {
        "ExportDescription": {
            "ExportArn": "arn:aws:dynamodb:region:account-id:table/test_table/export",
            "ExportStatus": "COMPLETED",
        }
    }

    mocker.patch(
        "pipeline.seeding.export.get_dynamodb_client", return_value=mock_ddb_client
    )

    result = is_export_complete(
        "arn:aws:dynamodb:region:account-id:table/test_table/export"
    )

    assert result is True
    mock_ddb_client.describe_export.assert_called_once_with(
        ExportArn="arn:aws:dynamodb:region:account-id:table/test_table/export"
    )


def test_is_export_complete_unrecognised(mocker: MockerFixture) -> None:
    mock_ddb_client = mocker.MagicMock()
    mock_ddb_client.describe_export.return_value = {
        "ExportDescription": {
            "ExportArn": "arn:aws:dynamodb:region:account-id:table/test_table/export",
            "ExportStatus": "ERRORED",
        }
    }

    mocker.patch(
        "pipeline.seeding.export.get_dynamodb_client", return_value=mock_ddb_client
    )

    with pytest.raises(ValueError, match="Unexpected export status: ERRORED"):
        is_export_complete("arn:aws:dynamodb:region:account-id:table/test_table/export")

    mock_ddb_client.describe_export.assert_called_once_with(
        ExportArn="arn:aws:dynamodb:region:account-id:table/test_table/export"
    )


@pytest.mark.asyncio
async def test_export_table(mocker: MockerFixture) -> None:
    mock_trigger = mocker.patch("pipeline.seeding.export.trigger_table_export")
    mock_trigger.return_value = {
        "ExportArn": "arn:aws:dynamodb:region:account-id:table/test_table/export",
        "S3Bucket": "test_s3_bucket_name",
    }

    mock_is_export_complete = mocker.patch("pipeline.seeding.export.is_export_complete")
    mock_is_export_complete.side_effect = [False, True]

    mock_ddb_client = mocker.MagicMock()
    mock_ddb_client.describe_export.return_value = {
        "ExportDescription": {
            "ExportArn": "arn:aws:dynamodb:region:account-id:table/test_table/export",
            "ExportStatus": "COMPLETED",
        }
    }
    mocker.patch(
        "pipeline.seeding.export.get_dynamodb_client", return_value=mock_ddb_client
    )

    mock_sleep = mocker.patch("pipeline.seeding.export.asyncio.sleep")
    mock_sleep.return_value = None

    response = await export_table("organisation", "local", "test-workspace")
    assert response == {
        "ExportArn": "arn:aws:dynamodb:region:account-id:table/test_table/export",
        "ExportStatus": "COMPLETED",
    }

    mock_trigger.assert_called_once_with(
        "ftrs-dos-local-database-organisation-test-workspace",
        "ftrs-dos-local-data-migration-pipeline-store-test-workspace",
    )
    mock_is_export_complete.assert_called_with(
        "arn:aws:dynamodb:region:account-id:table/test_table/export"
    )
    mock_sleep.assert_called()


@pytest.mark.asyncio
async def test_process_export(mocker: MockerFixture) -> None:
    get_file_list_mock = mocker.patch("pipeline.seeding.export.get_export_file_list")
    get_file_list_mock.return_value = ["file1", "file2"]

    download_files_mock = mocker.patch(
        "pipeline.seeding.export.download_exported_files"
    )
    download_files_mock.return_value = [
        gzip.compress(b'{"Item": {"id": 1}}'),
        gzip.compress(b'{"Item": {"id": 2}}'),
    ]

    result = await process_export(
        {"S3Bucket": "test_s3_bucket_name", "ExportManifest": "test_export_manifest"}
    )

    assert isinstance(result, pd.DataFrame)

    assert result.to_dict(orient="records") == [
        {"data": '{"Item": {"id": 1}}'},
        {"data": '{"Item": {"id": 2}}'},
    ]


def test_get_export_file_list(mocker: MockerFixture) -> None:
    get_object_mock = mocker.patch("pipeline.seeding.export.S3_CLIENT.get_object")
    get_object_mock.side_effect = [
        {"Body": BytesIO(b'{"manifestFilesS3Key": "manifestFilesKey"}')},
        {
            "Body": BytesIO(
                b"""
                {"dataFileS3Key": "file1"}
                {"dataFileS3Key": "file2"}
                """
            )
        },
    ]

    result = get_export_file_list(
        {
            "S3Bucket": "test_s3_bucket_name",
            "ExportManifest": "descriptionExportManifest",
        }
    )

    assert result == [{"dataFileS3Key": "file1"}, {"dataFileS3Key": "file2"}]

    get_object_mock.assert_has_calls(
        [
            mocker.call(Bucket="test_s3_bucket_name", Key="descriptionExportManifest"),
            mocker.call(Bucket="test_s3_bucket_name", Key="manifestFilesKey"),
        ]
    )


def test_download_exported_files(mocker: MockerFixture) -> None:
    get_object_mock = mocker.patch("pipeline.seeding.export.S3_CLIENT.get_object")
    get_object_mock.side_effect = [
        {"Body": BytesIO(b'{"Item": {"id": 1}}')},
        {"Body": BytesIO(b'{"Item": {"id": 2}}')},
    ]

    result = download_exported_files(
        {
            "S3Bucket": "test_s3_bucket_name",
            "TableArn": "arn:aws:dynamodb:region:account-id:table/test_table",
        },
        [{"dataFileS3Key": "file1"}, {"dataFileS3Key": "file2"}],
    )

    assert result == [
        b'{"Item": {"id": 1}}',
        b'{"Item": {"id": 2}}',
    ]

    expected_call_count = 2
    assert get_object_mock.call_count == expected_call_count

    get_object_mock.assert_has_calls(
        [
            mocker.call(Bucket="test_s3_bucket_name", Key="file1"),
            mocker.call(Bucket="test_s3_bucket_name", Key="file2"),
        ]
    )


def test_decompress_and_parse_files() -> None:
    result = decompress_and_parse_files(
        [
            gzip.compress(
                b"""
                {"Item": {"id": 1}}
                {"Item": {"id": 2}}
                {"Item": {"id": 3}}
                """
            ),
            gzip.compress(
                b"""
                {"Item": {"id": 4}}
                {"Item": {"id": 5}}
                {"Item": {"id": 6}}
                """
            ),
        ]
    )

    assert result == [
        '{"Item": {"id": 1}}',
        '{"Item": {"id": 2}}',
        '{"Item": {"id": 3}}',
        '{"Item": {"id": 4}}',
        '{"Item": {"id": 5}}',
        '{"Item": {"id": 6}}',
    ]


@pytest.mark.asyncio
async def test_run_s3_export(mocker: MockerFixture) -> None:
    export_task_mock = mocker.patch("pipeline.seeding.export.export_table")
    process_export_mock = mocker.patch("pipeline.seeding.export.process_export")
    to_parquet_mock = mocker.patch("pipeline.seeding.export.wr.s3.to_parquet")
    mock_set_parameter = mocker.patch("pipeline.seeding.export.set_parameter")

    export_task_mock.side_effect = [
        {
            "TableArn": "arn:aws:dynamodb:region:account-id:table/test_table_1",
            "S3Bucket": "test_s3_bucket_name",
        },
        {
            "TableArn": "arn:aws:dynamodb:region:account-id:table/test_table_2",
            "S3Bucket": "test_s3_bucket_name",
        },
    ]
    mock_processed_exports = [mocker.Mock(shape=[1]), mocker.Mock(shape=[1])]
    process_export_mock.side_effect = mock_processed_exports

    await run_s3_export("local", "workspace")

    export_task_mock.assert_has_calls(
        [
            mocker.call("location", "local", "workspace"),
            mocker.call("organisation", "local", "workspace"),
        ]
    )

    process_export_mock.assert_has_calls(
        [
            mocker.call(
                {
                    "TableArn": "arn:aws:dynamodb:region:account-id:table/test_table_1",
                    "S3Bucket": "test_s3_bucket_name",
                }
            ),
            mocker.call(
                {
                    "TableArn": "arn:aws:dynamodb:region:account-id:table/test_table_2",
                    "S3Bucket": "test_s3_bucket_name",
                }
            ),
        ],
        any_order=True,
    )

    to_parquet_mock.assert_has_calls(
        [
            mocker.call(
                df=mock_processed_exports[0],
                path="s3://test_s3_bucket_name/backups/test_table_1.parquet",
                dataset=False,
            ),
            mocker.call(
                df=mock_processed_exports[1],
                path="s3://test_s3_bucket_name/backups/test_table_2.parquet",
                dataset=False,
            ),
        ]
    )

    mock_set_parameter.assert_called_once_with(
        name="/ftrs-dos/local/dynamodb-backup-arns",
        value=json.dumps(
            {
                "test_table_1": "s3://test_s3_bucket_name/backups/test_table_1.parquet",
                "test_table_2": "s3://test_s3_bucket_name/backups/test_table_2.parquet",
            }
        ),
        overwrite=True,
    )
