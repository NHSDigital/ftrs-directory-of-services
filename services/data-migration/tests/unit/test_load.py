from pathlib import Path
from unittest.mock import call

import pandas as pd
import pytest
from ftrs_data_layer.models import DBModel, HealthcareService, Location, Organisation
from pytest_mock import MockerFixture

from pipeline.constants import TargetEnvironment
from pipeline.load import TABLE, get_table_name, load, save_to_table
from pipeline.utils.file_io import PathType
from tests.unit.test_transform import (
    transformed_GP_Practice_HS,
    transformed_GP_Practice_Loc,
    transformed_GP_Practice_Org,
)


@pytest.mark.parametrize(
    "table_to_save, expected_output",
    [
        (TABLE.ORGANISATION, Organisation(**transformed_GP_Practice_Org)),
        (TABLE.LOCATION, Location(**transformed_GP_Practice_Loc)),
        (TABLE.SERVICE, HealthcareService(**transformed_GP_Practice_HS)),
    ],
)
def test_save_to_table_organisation(
    mocker: MockerFixture, table_to_save: TABLE, expected_output: DBModel
) -> None:
    """
    Test save_to_table function with organisations
    """

    mock_repository_create = mocker.patch(
        "pipeline.load.DocumentLevelRepository.create"
    )

    input_df = pd.DataFrame(
        {
            "organisation": [transformed_GP_Practice_Org],
            "location": [transformed_GP_Practice_Loc],
            "healthcare-service": [transformed_GP_Practice_HS],
        }
    )
    table_name = "test-table"

    save_to_table(
        input_df=input_df,
        table=table_to_save,
        table_name=table_name,
        endpoint_url=None,
    )

    expected_create_calls = [expected_output]
    assert mock_repository_create.call_count == len(expected_create_calls)
    mock_repository_create.assert_has_calls(
        [call(org) for org in expected_create_calls],
        any_order=True,
    )


def test_load(mocker: MockerFixture, mock_tmp_directory: Path) -> None:
    input_df = pd.DataFrame(
        {
            "organisation": [transformed_GP_Practice_Org],
            "location": [transformed_GP_Practice_Loc],
            "healthcare-service": [transformed_GP_Practice_HS],
        }
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
        Organisation(**transformed_GP_Practice_Org),
        Location(**transformed_GP_Practice_Loc),
        HealthcareService(**transformed_GP_Practice_HS),
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
        ("organisation", "local", None, "ftrs-dos-local-database-organisation"),
        ("organisation", "dev", "test", "ftrs-dos-dev-database-organisation-test"),
        ("service", "prod", None, "ftrs-dos-prod-database-service"),
        ("service", "qa", "workspace1", "ftrs-dos-qa-database-service-workspace1"),
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
