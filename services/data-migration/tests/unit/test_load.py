from pathlib import Path
from unittest.mock import call

import pandas as pd
import pytest
from ftrs_data_layer.models import Organisation
from pytest_mock import MockerFixture

from pipeline.constants import TargetEnvironment
from pipeline.load import TABLE, get_table_name, load, save_to_table
from pipeline.utils.file_io import PathType


def test_save_to_table_organisations(
    mocker: MockerFixture,
) -> None:
    """
    Test _load_organisations function.
    """

    mock_repository_create = mocker.patch(
        "pipeline.load.DocumentLevelRepository.create"
    )

    input_df = pd.DataFrame(
        [
            {
                "organisation": {
                    "id": "d5a852ef-12c7-4014-b398-661716a63027",
                    "name": "Test Org",
                    "active": True,
                    "type": "GP Practice",
                    "createdBy": "ROBOT",
                    "createdDateTime": "2023-10-01T00:00:00Z",
                    "modifiedBy": "ROBOT",
                    "modifiedDateTime": "2023-10-01T00:00:00Z",
                }
            },
            {
                "organisation": {
                    "id": "4e7084db-e987-4241-a737-252bedfcc09c",
                    "name": "Another Org",
                    "active": True,
                    "type": "GP Practice",
                    "createdBy": "ROBOT",
                    "createdDateTime": "2023-10-01T00:00:00Z",
                    "modifiedBy": "ROBOT",
                    "modifiedDateTime": "2023-10-01T00:00:00Z",
                }
            },
        ]
    )
    table_name = "test-table"

    save_to_table(
        input_df=input_df,
        table=TABLE.ORGANISATION,
        table_name=table_name,
        endpoint_url=None,
    )

    expected_create_calls = [
        Organisation(
            id="d5a852ef-12c7-4014-b398-661716a63027",
            name="Test Org",
            active=True,
            type="GP Practice",
            createdBy="ROBOT",
            createdDateTime="2023-10-01T00:00:00Z",
            modifiedBy="ROBOT",
            modifiedDateTime="2023-10-01T00:00:00Z",
        ),
        Organisation(
            id="4e7084db-e987-4241-a737-252bedfcc09c",
            name="Another Org",
            active=True,
            type="GP Practice",
            createdBy="ROBOT",
            createdDateTime="2023-10-01T00:00:00Z",
            modifiedBy="ROBOT",
            modifiedDateTime="2023-10-01T00:00:00Z",
        ),
    ]
    assert mock_repository_create.call_count == len(expected_create_calls)
    mock_repository_create.assert_has_calls(
        [call(org) for org in expected_create_calls],
        any_order=True,
    )


def test_load(mocker: MockerFixture, mock_tmp_directory: Path) -> None:
    input_df = pd.DataFrame(
        [
            {
                "organisation": {
                    "id": "d5a852ef-12c7-4014-b398-661716a63027",
                    "name": "Test Org",
                    "active": True,
                    "type": "GP Practice",
                    "createdBy": "ROBOT",
                    "createdDateTime": "2023-10-01T00:00:00Z",
                    "modifiedBy": "ROBOT",
                    "modifiedDateTime": "2023-10-01T00:00:00Z",
                }
            },
        ]
    )
    input_path = mock_tmp_directory / "dos-gp-practice-transform.parquet"
    input_df.to_parquet(input_path, index=False)

    create_mock = mocker.patch(
        "pipeline.load.DocumentLevelRepository.create",
        return_value=None,
    )

    result = load(
        env=TargetEnvironment.local,
        workspace="test",
        input=str(input_path),
        endpoint_url="http://localhost:8000",
    )

    assert result is None

    expected_create_calls = [
        Organisation(
            id="d5a852ef-12c7-4014-b398-661716a63027",
            name="Test Org",
            active=True,
            type="GP Practice",
            createdBy="ROBOT",
            createdDateTime="2023-10-01T00:00:00Z",
            modifiedBy="ROBOT",
            modifiedDateTime="2023-10-01T00:00:00Z",
        ),
    ]
    assert create_mock.call_count == len(expected_create_calls)
    create_mock.assert_has_calls(
        [call(org) for org in expected_create_calls],
        any_order=True,
    )


def test_load_s3(
    mocker: MockerFixture,
) -> None:
    mock_check_bucket = mocker.patch(
        "pipeline.utils.validators.check_bucket_access",
        return_value=True,
    )
    mock_check_object = mocker.patch(
        "pipeline.utils.validators.check_object_exists",
        return_value=True,
    )
    mock_read = mocker.patch(
        "pipeline.load.read_parquet_file", return_value=pd.DataFrame()
    )
    mocker.patch("pipeline.load.save_to_table")

    s3_uri = "s3://your-bucket-name/path/to/object.parquet"

    load(
        env=TargetEnvironment.local,
        workspace="test",
        input=s3_uri,
        endpoint_url="http://localhost:8000",
    )

    mock_check_bucket.assert_called_once_with("your-bucket-name")
    mock_check_object.assert_called_once_with(
        "your-bucket-name",
        "path/to/object.parquet",
    )
    mock_read.assert_called_once_with(
        PathType.S3,
        s3_uri,
    )


@pytest.mark.parametrize(
    "entity_type, env, workspace, expected_table_name",
    [
        ("organisation", "local", None, "ftrs-dos-db-local-organisation"),
        ("organisation", "dev", "test", "ftrs-dos-db-dev-organisation-test"),
        ("service", "prod", None, "ftrs-dos-db-prod-service"),
        ("service", "qa", "workspace1", "ftrs-dos-db-qa-service-workspace1"),
    ],
)
def test_get_table_name(
    entity_type: str, env: str, workspace: str | None, expected_table_name: str
) -> None:
    """
    Test get_table_name function with various inputs.
    """
    result = get_table_name(entity_type, env, workspace)
    assert result == expected_table_name
