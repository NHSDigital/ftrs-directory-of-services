import json
import os
from functools import cache

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.http_client import build_headers, make_request
from common.secrets import get_ods_terminology_api_key

ods_client_logger = Logger.get(service="ods_client")


@cache
def get_base_ods_terminology_api_url() -> str:
    env = os.environ.get("ENVIRONMENT", "local")

    if env == "local":
        return os.environ.get(
            "LOCAL_ODS_URL",
            "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        )

    ods_url = os.environ.get("ODS_URL")
    if ods_url is None:
        err_msg = "ODS_URL environment variable is not set"
        ods_client_logger.log(
            OdsETLPipelineLogBase.ETL_UTILS_004,
            method="GET",
            url="ODS_URL",
            error_message=err_msg,
        )
        raise KeyError(err_msg)
    return ods_url


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
