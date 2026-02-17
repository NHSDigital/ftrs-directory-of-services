from http import HTTPStatus
from unittest.mock import MagicMock, patch

from dos_ingest.handler import handler


def test_handler_delegates_to_mangum() -> None:
    event = {"headers": {"X-Request-ID": "req-123"}}
    context = MagicMock()

    with patch("dos_ingest.handler.Mangum") as mangum_cls:
        mangum_instance = MagicMock()
        mangum_instance.return_value = {"statusCode": 200, "body": "ok"}
        mangum_cls.return_value = mangum_instance

        response = handler(event, context)

    assert response["statusCode"] == HTTPStatus.OK
    mangum_cls.assert_called_once()
    mangum_instance.assert_called_once_with(event, context)
