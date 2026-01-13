import json

from ftrs_common.logger import Logger

from common.http_client import build_headers, make_request
from common.secrets import get_ods_terminology_api_key

ods_client_logger = Logger.get(service="ods_client")


def make_ods_request(
    url: str,
    method: str = "GET",
    params: dict | None = None,
    **kwargs: dict,
) -> dict:
    json_data = kwargs.get("json")
    json_string = json.dumps(json_data) if json_data is not None else None

    api_key = get_ods_terminology_api_key()

    headers = build_headers(
        json_data=json_data,
        json_string=json_string,
        api_key=api_key,
    )

    return make_request(
        url=url,
        method=method,
        params=params,
        headers=headers,
        **kwargs,
    )
