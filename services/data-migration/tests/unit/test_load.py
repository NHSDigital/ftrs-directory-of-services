from pathlib import Path
from unittest.mock import Mock, call

import pandas as pd
import pytest
from ftrs_data_layer.models import Organisation
from ftrs_data_layer.repository.dynamodb import DocumentLevelRepository
from pytest_mock import MockerFixture

from pipeline.common import TargetEnvironment
from pipeline.load import (
    _load_organisations,
    _retrieve_gp_practice_data,
    load,
)


def test_retrieve_gp_practice_data(
    mocker: MockerFixture, mock_tmp_directory: Path
) -> None:
    test_file = mock_tmp_directory / "dos-gp-practice-transform.parquet"
    test_file.touch()

    mocker.patch(
        "pipeline.load.pd.read_parquet", return_value=pd.DataFrame(["Test Data"])
    )

    result = _retrieve_gp_practice_data(mock_tmp_directory)
    assert result == [{0: "Test Data"}]


def test_retrieve_gp_practice_data_no_file(mock_tmp_directory: Path) -> None:
    """
    Test _retrieve_gp_practice_data function when file does not exist.
    """

    with pytest.raises(FileNotFoundError) as excinfo:
        _retrieve_gp_practice_data(mock_tmp_directory)

    assert (
        str(excinfo.value)
        == f"File not found: {mock_tmp_directory}/dos-gp-practice-transform.parquet"
    )


def test_load_organisations(
    mock_logging: Mock,
) -> None:
    """
    Test _load_organisations function.
    """

    mock_repository = DocumentLevelRepository
    mock_repository.create = Mock()

    input_df = [
        pd.Series(
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
            }
        ),
        pd.Series(
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
            }
        ),
    ]
    table_name = "test-table"

    _load_organisations(
        input_df=input_df,
        table_name=table_name,
        endpoint_url=None,
        repository_cls=mock_repository,
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
    assert mock_repository.create.call_count == len(expected_create_calls)
    mock_repository.create.assert_has_calls(
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
        input_path=mock_tmp_directory,
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
