import os
from functools import cache

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

url_config_logger = Logger.get(service="ods_url_config")


@cache
def get_base_apim_api_url() -> str:
    """Get the base APIM API URL based on environment configuration."""
    env = os.environ.get("ENVIRONMENT", "local")

    if env == "local":
        return os.environ["LOCAL_APIM_API_URL"]

    return os.environ.get("APIM_URL")


@cache
def get_base_ods_terminology_api_url() -> str:
    """Get the base ODS Terminology API URL based on environment configuration."""
    env = os.environ.get("ENVIRONMENT", "local")

    if env == "local":
        return os.environ.get(
            "LOCAL_ODS_URL",
            "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        )

    ods_url = os.environ.get("ODS_URL")
    if ods_url is None:
        err_msg = "ODS_URL environment variable is not set"
        url_config_logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_011,
            secret_name="ODS_URL",
            error_message=err_msg,
        )
        raise KeyError(err_msg)
    return ods_url
