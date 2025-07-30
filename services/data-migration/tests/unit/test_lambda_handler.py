from aws_lambda_powertools.utilities.data_classes import SQSEvent
from pytest_mock import MockerFixture

from pipeline.application import DataMigrationApplication, DMSEvent
from pipeline.lambda_handler import lambda_handler
from pipeline.utils.config import DataMigrationConfig


def test_lambda_handler(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
) -> None:
    app = DataMigrationApplication(config=mock_config)
    app.handle_dms_event = mocker.MagicMock()

    mocker.patch("pipeline.lambda_handler.DataMigrationApplication", return_value=app)

    event = SQSEvent(
        data={
            "Records": [
                {
                    "body": '{"type": "dms_event", "record_id": 1, "table_name": "test_table", "method": "insert"}'
                },
                {
                    "body": '{"type": "dms_event", "record_id": 2, "table_name": "test_table", "method": "update"}'
                },
            ]
        }
    )

    context = {}

    lambda_handler(event, context)

    app.handle_dms_event.assert_has_calls(
        [
            mocker.call(
                DMSEvent(
                    type="dms_event",
                    record_id=1,
                    table_name="test_table",
                    method="insert",
                )
            ),
            mocker.call(
                DMSEvent(
                    type="dms_event",
                    record_id=2,
                    table_name="test_table",
                    method="update",
                )
            ),
        ]
    )
