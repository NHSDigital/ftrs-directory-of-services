from pathlib import Path

import pandas as pd
import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from pipeline.transform import transform
from pipeline.utils.file_io import PathType


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
                    "uid": "00000000-0000-0000-0000-000000000000",
                    "serviceid": 192040,
                    "publicphone": "0000 8888",
                    "nonpublicphone": "12345678901",
                    "email": "test@nhs.net",
                    "web": "www.test.co.uk",
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
                            "createdDateTime": "2025-03-27T12:00:00Z",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00Z",
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
                                    "createdDateTime": "2025-03-27T12:00:00Z",
                                    "modifiedBy": "ROBOT",
                                    "modifiedDateTime": "2025-03-27T12:00:00Z",
                                }
                            ],
                        },
                    ],
                    "healthcare-service": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "createdBy": "ROBOT",
                            "createdDateTime": "2025-03-27T12:00:00Z",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00Z",
                            "identifier_oldDoS_uid": "00000000-0000-0000-0000-000000000000",
                            "active": True,
                            "category": "unknown",
                            "providedBy": "123e4567-e89b-12d3-a456-426614174000",
                            "location": None,
                            "name": "Test Org",
                            "telecom": {
                                "phone_public": "0000 8888",
                                "phone_private": "12345678901",
                                "email": "test@nhs.net",
                                "web": "www.test.co.uk",
                            },
                            "type": "GP Practice",
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
                    "uid": "00000000-0000-0000-0000-000000000000",
                    "serviceid": 192040,
                    "publicphone": "0000 8888",
                    "nonpublicphone": "12345678901",
                    "email": "test@nhs.net",
                    "web": "www.test.co.uk",
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
                            "createdDateTime": "2025-03-27T12:00:00Z",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00Z",
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
                                    "createdDateTime": "2025-03-27T12:00:00Z",
                                    "modifiedBy": "ROBOT",
                                    "modifiedDateTime": "2025-03-27T12:00:00Z",
                                }
                            ],
                        }
                    ],
                    "healthcare-service": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "createdBy": "ROBOT",
                            "createdDateTime": "2025-03-27T12:00:00Z",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00Z",
                            "identifier_oldDoS_uid": "00000000-0000-0000-0000-000000000000",
                            "active": True,
                            "category": "unknown",
                            "providedBy": "123e4567-e89b-12d3-a456-426614174000",
                            "location": None,
                            "name": "Test Org",
                            "telecom": {
                                "phone_public": "0000 8888",
                                "phone_private": "12345678901",
                                "email": "test@nhs.net",
                                "web": "www.test.co.uk",
                            },
                            "type": "GP Practice",
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
                    "uid": "00000000-0000-0000-0000-000000000000",
                    "serviceid": 192040,
                    "publicphone": "0000 8888",
                    "nonpublicphone": "12345678901",
                    "email": "test@nhs.net",
                    "web": "www.test.co.uk",
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
                            "createdDateTime": "2025-03-27T12:00:00Z",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00Z",
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
                                    "createdDateTime": "2025-03-27T12:00:00Z",
                                    "modifiedBy": "ROBOT",
                                    "modifiedDateTime": "2025-03-27T12:00:00Z",
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
                                    "createdDateTime": "2025-03-27T12:00:00Z",
                                    "modifiedBy": "ROBOT",
                                    "modifiedDateTime": "2025-03-27T12:00:00Z",
                                },
                            ],
                        },
                    ],
                    "healthcare-service": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "createdBy": "ROBOT",
                            "createdDateTime": "2025-03-27T12:00:00Z",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00Z",
                            "identifier_oldDoS_uid": "00000000-0000-0000-0000-000000000000",
                            "active": True,
                            "category": "unknown",
                            "providedBy": "123e4567-e89b-12d3-a456-426614174000",
                            "location": None,
                            "name": "Org 1",
                            "telecom": {
                                "phone_public": "0000 8888",
                                "phone_private": "12345678901",
                                "email": "test@nhs.net",
                                "web": "www.test.co.uk",
                            },
                            "type": "GP Practice",
                        }
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
                    "uid": "00000000-0000-0000-0000-000000000000",
                    "serviceid": 192040,
                    "publicphone": "0000 8888",
                    "nonpublicphone": "12345678901",
                    "email": "test@nhs.net",
                    "web": "www.test.co.uk",
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
                            "createdDateTime": "2025-03-27T12:00:00Z",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00Z",
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
                                    "createdDateTime": "2025-03-27T12:00:00Z",
                                    "modifiedBy": "ROBOT",
                                    "modifiedDateTime": "2025-03-27T12:00:00Z",
                                }
                            ],
                        }
                    ],
                    "healthcare-service": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "createdBy": "ROBOT",
                            "createdDateTime": "2025-03-27T12:00:00Z",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00Z",
                            "identifier_oldDoS_uid": "00000000-0000-0000-0000-000000000000",
                            "active": True,
                            "category": "unknown",
                            "providedBy": "123e4567-e89b-12d3-a456-426614174000",
                            "location": None,
                            "name": "Test Org",
                            "telecom": {
                                "phone_public": "0000 8888",
                                "phone_private": "12345678901",
                                "email": "test@nhs.net",
                                "web": "www.test.co.uk",
                            },
                            "type": "GP Practice",
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
                    "uid": "00000000-0000-0000-0000-000000000000",
                    "serviceid": 192040,
                    "publicphone": "0000 8888",
                    "nonpublicphone": "12345678901",
                    "email": "test@nhs.net",
                    "web": "www.test.co.uk",
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
                            "createdDateTime": "2025-03-27T12:00:00Z",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00Z",
                            "endpoints": [],
                        }
                    ],
                    "healthcare-service": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "createdBy": "ROBOT",
                            "createdDateTime": "2025-03-27T12:00:00Z",
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": "2025-03-27T12:00:00Z",
                            "identifier_oldDoS_uid": "00000000-0000-0000-0000-000000000000",
                            "active": True,
                            "category": "unknown",
                            "providedBy": "123e4567-e89b-12d3-a456-426614174000",
                            "location": None,
                            "name": "Test Org",
                            "telecom": {
                                "phone_public": "0000 8888",
                                "phone_private": "12345678901",
                                "email": "test@nhs.net",
                                "web": "www.test.co.uk",
                            },
                            "type": "GP Practice",
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
    mock_tmp_directory: Path,
) -> None:
    """
    Test the transform function to ensure input data is transformed correctly.
    """
    input_path = mock_tmp_directory / "input.parquet"
    output_path = mock_tmp_directory / "output.parquet"

    input_path.touch()

    assert input_path.exists()
    assert not output_path.exists()

    read_mock = mocker.patch(
        "pipeline.transform.read_parquet_file", return_value=input_data
    )
    mocker.patch(
        "ftrs_data_layer.models.uuid4",
        return_value="123e4567-e89b-12d3-a456-426614174000",
    )
    write_mock = mocker.patch("pipeline.transform.write_parquet_file")

    transform(input=str(input_path), output=str(output_path))

    read_mock.assert_called_once_with(PathType.FILE, input_path)
    write_mock.assert_called_once()

    file_type, file_path, gp_practice_df = write_mock.call_args[0]

    assert file_type == PathType.FILE
    assert file_path == output_path
    assert isinstance(gp_practice_df, pd.DataFrame)
    assert not gp_practice_df.empty
    assert gp_practice_df.shape[0] == expected_output.shape[0], "Row count mismatch"

    for idx, row in gp_practice_df.iterrows():
        row_dict = row.to_dict()
        expected_row_dict = expected_output.iloc[idx].to_dict()

        assert row_dict == expected_row_dict, (
            f"Row {idx} mismatch: {row_dict} != {expected_row_dict}"
        )


def test_transform_empty_dataframe(
    mocker: MockerFixture, mock_tmp_directory: Path
) -> None:
    """
    Test the transform function with an empty DataFrame.
    """
    input_path = mock_tmp_directory / "mock_input_path"
    output_path = mock_tmp_directory / "mock_output_path"
    input_path.touch()

    mocker.patch("pipeline.transform.read_parquet_file", return_value=pd.DataFrame())

    with pytest.raises(ValueError) as excinfo:
        transform(input=str(input_path), output=str(output_path))

    assert str(excinfo.value) == "No data found in the input DataFrame"


def test_read_s3(
    mocker: MockerFixture,
    mock_tmp_directory: Path,
) -> None:
    mock_bucket_access = mocker.patch(
        "pipeline.utils.validators.check_bucket_access", return_value=True
    )
    mock_check_object = mocker.patch(
        "pipeline.utils.validators.check_object_exists", return_value=True
    )
    mock_read = mocker.patch(
        "pipeline.transform.read_parquet_file", return_value=pd.DataFrame()
    )
    mocker.patch("pipeline.transform.transform_gp_practices")

    output_path = mock_tmp_directory / "output.parquet"
    s3_uri = "s3://your-bucket-name/path/to/object/input.parquet"

    transform(input=str(s3_uri), output=str(output_path))

    mock_read.assert_called_once_with(PathType.S3, s3_uri)

    mock_bucket_access.assert_called_once_with("your-bucket-name")
    mock_check_object.assert_called_once_with(
        "your-bucket-name", "path/to/object/input.parquet"
    )


def test_write_s3(
    mocker: MockerFixture,
    mock_tmp_directory: Path,
) -> None:
    mock_bucket_access = mocker.patch(
        "pipeline.utils.validators.check_bucket_access", return_value=True
    )
    mock_check_object = mocker.patch(
        "pipeline.utils.validators.check_object_exists", return_value=False
    )

    mock_read = mocker.patch(
        "pipeline.transform.read_parquet_file", return_value=pd.DataFrame()
    )
    mock_write = mocker.patch("pipeline.transform.write_parquet_file")
    mocker.patch("pipeline.transform.transform_gp_practices", return_value="TestOutput")

    input_path = mock_tmp_directory / "input.parquet"
    input_path.touch()

    s3_uri = "s3://your-bucket-name/path/to/object/output.parquet"

    transform(input=str(input_path), output=str(s3_uri))

    mock_bucket_access.assert_called_once_with("your-bucket-name")
    mock_check_object.assert_called_once_with(
        "your-bucket-name", "path/to/object/output.parquet"
    )

    mock_read.assert_called_once_with(PathType.FILE, input_path)
    mock_write.assert_called_once_with(PathType.S3, s3_uri, "TestOutput")
