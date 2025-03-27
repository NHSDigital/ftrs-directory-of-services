from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from pipeline.transform import main, transform


def test_main_parses_args(mocker: MockerFixture) -> None:
    """
    Test that main parses command line arguments and calls transform with the correct arguments
    """
    transform_mock = mocker.patch("pipeline.transform.transform")
    args = ["--input-path", "test_input_path", "--output-path", "test_output_path"]

    main(args)

    assert transform_mock.called is True
    assert transform_mock.call_args[0][0] == Path("test_input_path")
    assert transform_mock.call_args[0][1] == Path("test_output_path")


def test_main_throws_error_on_no_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when no arguments are provided
    """
    expected_exit_code = 2

    transform_mock = mocker.patch("pipeline.transform.transform")
    args = [""]
    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert transform_mock.called is False


def test_main_throws_error_on_missing_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when required arguments are missing
    """
    expected_exit_code = 2

    transform_mock = mocker.patch("pipeline.transform.transform")
    args = ["--output-path", "test_output_path"]
    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert transform_mock.called is False


def test_main_throws_error_on_invalid_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when invalid arguments are
    """
    expected_exit_code = 2

    transform_mock = mocker.patch("pipeline.transform.transform")
    args = [
        "--input-path",
        "test_input_path",
        "--output-path",
        "test_output_path",
        "--invalid-arg",
    ]
    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert transform_mock.called is False


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
                                "endpointid": "1",
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
                            "createdDateTime": datetime(2025, 3, 27, 12, 0),
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": datetime(2025, 3, 27, 12, 0),
                        }
                    ],
                    "endpoints": [
                        [
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
                                "createdDateTime": datetime(2025, 3, 27, 12, 0),
                                "modifiedBy": "ROBOT",
                                "modifiedDateTime": datetime(2025, 3, 27, 12, 0),
                            }
                        ]
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
                                "endpointid": "2",
                                "transport": "sms",
                                "businessscenario": "scenario2",
                                "interaction": "interaction2",
                                "address": "address2",
                                "endpointorder": 2,
                                "iscompressionenabled": "compressed",
                                "format": "XML",
                            }
                        ],
                        [
                            {
                                "endpointid": "3",
                                "transport": "fax",
                                "businessscenario": "scenario3",
                                "interaction": "interaction3",
                                "address": "address3",
                                "endpointorder": 3,
                                "iscompressionenabled": "uncompressed",
                                "format": "TXT",
                            }
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
                            "createdDateTime": datetime(2025, 3, 27, 12, 0),
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": datetime(2025, 3, 27, 12, 0),
                        },
                    ],
                    "endpoints": [
                        [
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
                                "createdDateTime": datetime(2025, 3, 27, 12, 0),
                                "modifiedBy": "ROBOT",
                                "modifiedDateTime": datetime(2025, 3, 27, 12, 0),
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
                                "createdDateTime": datetime(2025, 3, 27, 12, 0),
                                "modifiedBy": "ROBOT",
                                "modifiedDateTime": datetime(2025, 3, 27, 12, 0),
                            },
                        ],
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
                                "endpointid": "1",
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
                            "createdDateTime": datetime(2025, 3, 27, 12, 0),
                            "modifiedBy": "ROBOT",
                            "modifiedDateTime": datetime(2025, 3, 27, 12, 0),
                        }
                    ],
                    "endpoints": [
                        [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "identifier_oldDoS_id": 1,
                                "status": "active",
                                "connectionType": "telno",
                                "name": None,
                                "description": "scenario1",
                                "payloadType": "",
                                "address": "address1",
                                "managedByOrganisation": "123e4567-e89b-12d3-a456-426614174000",
                                "service": None,
                                "order": 1,
                                "isCompressionEnabled": False,
                                "format": "",
                                "createdBy": "ROBOT",
                                "createdDateTime": datetime(2025, 3, 27, 12, 0),
                                "modifiedBy": "ROBOT",
                                "modifiedDateTime": datetime(2025, 3, 27, 12, 0),
                            }
                        ]
                    ],
                }
            ),
        ),
    ],
)
def test_transform(
    mocker: MockerFixture, input_data: pd.DataFrame, expected_output: pd.DataFrame
) -> None:
    """
    Test the transform function to ensure input data is transformed correctly.
    """

    input_path = Path("mock_input_path")
    output_path = Path("mock_output_path")

    mocker.patch("pandas.read_parquet", return_value=input_data)

    captured_df = None

    def capture_to_parquet(self: pd.DataFrame, *args: tuple, **kwargs: dict) -> None:
        nonlocal captured_df
        captured_df = self

    mocker.patch.object(pd.DataFrame, "to_parquet", new=capture_to_parquet)

    mocker.patch(
        "pipeline.transform.uuid4", return_value="123e4567-e89b-12d3-a456-426614174000"
    )
    mocker.patch(
        "pipeline.transform.datetime",
        **{"now.return_value.strftime.return_value": datetime(2025, 3, 27, 12, 0)},
    )

    transform(input_path, output_path)

    assert captured_df is not None, "The DataFrame was not captured."
    pd.testing.assert_frame_equal(captured_df, expected_output)
