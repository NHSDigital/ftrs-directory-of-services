import io
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pandas as pd
import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from pipeline.common import Constants
from pipeline.exceptions import InvalidArgumentsError, S3BucketAccessError
from pipeline.transform import transform, put_object_to_s3


@freeze_time("2025-03-27 12:00:00")
@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        (
            # Input data
            pd.DataFrame(
                {
                    "odscode": ["A123"],
                    "name": ["Test Org"],
                    "type": ["GP Practice"],
                    "endpoints": [
                        [
                            {
                                "id": "1",
                                "transport": "email",
                                "businessscenario": "scenario1",
                                "interaction": "interaction1",
                                "address": "address1",
                                "endpointorder": 1,
                                "iscompressionenabled": "uncompressed",
                                "format": "PDF",
                            }
                        ]
                    ],
                }
            ),
            # Expected output
            pd.DataFrame(
                {
                    "organisation": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "identifier_ODS_ODSCode": "A123",
                            "active": True,
                            "name": "Test Org",
                            "telecom": None,
                            "type": "GP Practice",
                            "createdBy": "ROBOT",
                            "createdDateTime": "2025-03-27T12:00:00",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00",
                            "endpoints": [
                                {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "identifier_oldDoS_id": 1,
                                    "status": "active",
                                    "connectionType": "email",
                                    "name": None,
                                    "description": "scenario1",
                                    "format": "PDF",
                                    "payloadType": "interaction1",
                                    "address": "address1",
                                    "managedByOrganisation": "123e4567-e89b-12d3-a456-426614174000",
                                    "service": None,
                                    "order": 1,
                                    "isCompressionEnabled": False,
                                    "createdBy": "ROBOT",
                                    "createdDateTime": "2025-03-27T12:00:00",
                                    "modifiedBy": "ROBOT",
                                    "modifiedDateTime": "2025-03-27T12:00:00",
                                }
                            ],
                        }
                    ],
                }
            ),
        ),
        (
            # Input data
            pd.DataFrame(
                {
                    "odscode": ["A123"],
                    "name": ["Test Org"],
                    "type": ["GP Practice"],
                    "endpoints": [
                        [
                            {
                                "id": "1",
                                "transport": "email",
                                "businessscenario": "scenario1",
                                "interaction": "interaction1",
                                "address": "address1",
                                "endpointorder": 1,
                                "iscompressionenabled": "uncompressed",
                                "format": "PDF",
                            }
                        ]
                    ],
                }
            ),
            # Expected output
            pd.DataFrame(
                {
                    "organisation": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "identifier_ODS_ODSCode": "A123",
                            "active": True,
                            "name": "Test Org",
                            "telecom": None,
                            "type": "GP Practice",
                            "createdBy": "ROBOT",
                            "createdDateTime": "2025-03-27T12:00:00",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00",
                            "endpoints": [
                                {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "identifier_oldDoS_id": 1,
                                    "status": "active",
                                    "connectionType": "email",
                                    "name": None,
                                    "description": "scenario1",
                                    "payloadType": "interaction1",
                                    "address": "address1",
                                    "managedByOrganisation": "123e4567-e89b-12d3-a456-426614174000",
                                    "service": None,
                                    "order": 1,
                                    "isCompressionEnabled": False,
                                    "format": "PDF",
                                    "createdBy": "ROBOT",
                                    "createdDateTime": "2025-03-27T12:00:00",
                                    "modifiedBy": "ROBOT",
                                    "modifiedDateTime": "2025-03-27T12:00:00",
                                }
                            ],
                        }
                    ],
                }
            ),
        ),
        (
            # Input data with multiple endpoints and varied compression settings
            pd.DataFrame(
                {
                    "odscode": "B456",
                    "name": "Org 1",
                    "type": "GP Practice",
                    "endpoints": [
                        [
                            {
                                "id": "2",
                                "transport": "sms",
                                "businessscenario": "scenario2",
                                "interaction": "interaction2",
                                "address": "address2",
                                "endpointorder": 2,
                                "iscompressionenabled": "compressed",
                                "format": "XML",
                            },
                            {
                                "id": "3",
                                "transport": "fax",
                                "businessscenario": "scenario3",
                                "interaction": "interaction3",
                                "address": "address3",
                                "endpointorder": 3,
                                "iscompressionenabled": "uncompressed",
                                "format": "TXT",
                            },
                        ],
                    ],
                }
            ),
            # Expected output
            pd.DataFrame(
                {
                    "organisation": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "identifier_ODS_ODSCode": "B456",
                            "active": True,
                            "name": "Org 1",
                            "telecom": None,
                            "type": "GP Practice",
                            "createdBy": "ROBOT",
                            "createdDateTime": "2025-03-27T12:00:00",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00",
                            "endpoints": [
                                {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "identifier_oldDoS_id": 2,
                                    "status": "active",
                                    "connectionType": "sms",
                                    "name": None,
                                    "description": "scenario2",
                                    "payloadType": "interaction2",
                                    "address": "address2",
                                    "managedByOrganisation": "123e4567-e89b-12d3-a456-426614174000",
                                    "service": None,
                                    "order": 2,
                                    "isCompressionEnabled": True,
                                    "format": "XML",
                                    "createdBy": "ROBOT",
                                    "createdDateTime": "2025-03-27T12:00:00",
                                    "modifiedBy": "ROBOT",
                                    "modifiedDateTime": "2025-03-27T12:00:00",
                                },
                                {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "identifier_oldDoS_id": 3,
                                    "status": "active",
                                    "connectionType": "fax",
                                    "name": None,
                                    "description": "scenario3",
                                    "payloadType": "interaction3",
                                    "address": "address3",
                                    "managedByOrganisation": "123e4567-e89b-12d3-a456-426614174000",
                                    "service": None,
                                    "order": 3,
                                    "isCompressionEnabled": False,
                                    "format": "TXT",
                                    "createdBy": "ROBOT",
                                    "createdDateTime": "2025-03-27T12:00:00",
                                    "modifiedBy": "ROBOT",
                                    "modifiedDateTime": "2025-03-27T12:00:00",
                                },
                            ],
                        },
                    ],
                },
            ),
        ),
        (
            # Input data with transport == telno
            pd.DataFrame(
                {
                    "odscode": ["C789"],
                    "name": ["Test Org"],
                    "type": ["GP Practice"],
                    "endpoints": [
                        [
                            {
                                "id": "1",
                                "transport": "telno",
                                "businessscenario": "scenario1",
                                "interaction": "interaction1",
                                "address": "address1",
                                "endpointorder": 1,
                                "iscompressionenabled": "uncompressed",
                                "format": "PDF",
                            }
                        ]
                    ],
                }
            ),
            # Expected output
            pd.DataFrame(
                {
                    "organisation": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "identifier_ODS_ODSCode": "C789",
                            "active": True,
                            "name": "Test Org",
                            "telecom": None,
                            "type": "GP Practice",
                            "createdBy": "ROBOT",
                            "createdDateTime": "2025-03-27T12:00:00",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00",
                            "endpoints": [
                                {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "identifier_oldDoS_id": 1,
                                    "status": "active",
                                    "connectionType": "telno",
                                    "name": None,
                                    "description": "scenario1",
                                    "payloadType": None,
                                    "address": "address1",
                                    "managedByOrganisation": "123e4567-e89b-12d3-a456-426614174000",
                                    "service": None,
                                    "order": 1,
                                    "isCompressionEnabled": False,
                                    "format": None,
                                    "createdBy": "ROBOT",
                                    "createdDateTime": "2025-03-27T12:00:00",
                                    "modifiedBy": "ROBOT",
                                    "modifiedDateTime": "2025-03-27T12:00:00",
                                }
                            ],
                        }
                    ],
                }
            ),
        ),
        (
            # Input data where endpoints is none
            pd.DataFrame(
                {
                    "odscode": ["A123"],
                    "name": ["Test Org"],
                    "type": ["GP Practice"],
                    "endpoints": [[]],
                }
            ),
            # Expected output
            pd.DataFrame(
                {
                    "organisation": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "identifier_ODS_ODSCode": "A123",
                            "active": True,
                            "name": "Test Org",
                            "telecom": None,
                            "type": "GP Practice",
                            "createdBy": "ROBOT",
                            "createdDateTime": "2025-03-27T12:00:00",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00",
                            "endpoints": [],
                        }
                    ],
                }
            ),
        ),
    ],
)
def test_transform(
    mocker: MockerFixture,
    input_data: pd.DataFrame,
    expected_output: pd.DataFrame,
    mock_pd_to_parquet: Mock,
    mock_tmp_directory: Path,
) -> None:
    """
    Test the transform function to ensure input data is transformed correctly.
    """

    mocker.patch("pandas.read_parquet", return_value=input_data)
    mocker.patch(
        "ftrs_data_layer.models.uuid4",
        return_value="123e4567-e89b-12d3-a456-426614174000",
    )

    input_path = mock_tmp_directory / "input.parquet"
    output_path = mock_tmp_directory / "output.parquet"

    result = transform(input_path, output_path)

    assert mock_pd_to_parquet.called, "pd.to_parquet was not called."

    gp_practice_df = result["dos-gp-practice-transform"]

    assert gp_practice_df is not None
    assert not gp_practice_df.empty
    assert gp_practice_df.shape[0] == expected_output.shape[0], "Row count mismatch"

    for idx, row in gp_practice_df.iterrows():
        row_dict = row.to_dict()
        expected_row_dict = expected_output.iloc[idx].to_dict()

        assert row_dict == expected_row_dict, (
            f"Row {idx} mismatch: {row_dict} != {expected_row_dict}"
        )


def test_transform_empty_dataframe(
    mocker: MockerFixture, mock_pd_to_parquet: Mock, mock_tmp_directory: Path
) -> None:
    """
    Test the transform function with an empty DataFrame.
    """

    input_path = mock_tmp_directory / "mock_input_path"
    output_path = mock_tmp_directory / "mock_output_path"

    mocker.patch("pandas.read_parquet", return_value=pd.DataFrame())

    with pytest.raises(ValueError) as excinfo:
        transform(input_path, output_path)

    assert not mock_pd_to_parquet.called
    assert str(excinfo.value) == "No data found in the input DataFrame"

def test_transform_invalid_arguments():
    input_path = Path("/path/to/input")
    output_path = None
    s3_output_uri = None

    with pytest.raises(InvalidArgumentsError):
        transform(input_path=input_path, output_path=output_path, s3_output_uri=s3_output_uri)

def test_transform_both_output_and_s3_uri():
    input_path = Path("/path/to/input")
    output_path = Path("/path/to/output")
    s3_output_uri = "s3://bucket/path"
    # Mock the function to raise InvalidArgumentsError
    with pytest.raises(InvalidArgumentsError):
        transform(input_path=input_path, output_path=output_path, s3_output_uri=s3_output_uri)

@pytest.fixture
def mock_dataframe():
    return pd.DataFrame({"column1": [1, 2], "column2": ["value1", "value2"]})

@freeze_time("2025-03-27 12:00:00")
@patch("pipeline.transform.BucketWrapper")
@patch("pipeline.transform.io.BytesIO", wraps=io.BytesIO)  # Use a real BytesIO object
def test_put_object_to_s3_success(mock_bytes_io, mock_bucket_wrapper):
    # Arrange
    mock_s3_bucket = MagicMock()
    mock_bucket_wrapper.return_value = mock_s3_bucket
    mock_s3_bucket.s3_bucket_exists.return_value = True

    s3_output_uri = "s3://test-bucket/test-path"
    input_path = Path("/dummy/path")
    Constants.GP_PRACTICE_TRANSFORM_FILE = "transformed_file.parquet"

    mock_dataframe = MagicMock()
    mock_dataframe.to_parquet = MagicMock()

    # Act
    put_object_to_s3(s3_output_uri, input_path, mock_dataframe)

    # Assert
    mock_s3_bucket.s3_bucket_exists.assert_called_once()
    mock_dataframe.to_parquet.assert_called_once()
    mock_s3_bucket.s3_upload_file.assert_called_once()

@patch("pipeline.transform.BucketWrapper")
def test_put_object_to_s3_bucket_not_exists(mock_bucket_wrapper):
    # Arrange
    mock_s3_bucket = MagicMock()
    mock_bucket_wrapper.return_value = mock_s3_bucket
    mock_s3_bucket.s3_bucket_exists.return_value = False

    s3_output_uri = "s3://test-bucket/test-path"
    input_path = Path("/dummy/path")

    # Act & Assert
    with pytest.raises(S3BucketAccessError, match="Bucket URI does not exist or you don't have access to it."):
        put_object_to_s3(s3_output_uri, input_path, MagicMock())

    mock_s3_bucket.s3_bucket_exists.assert_called_once()

