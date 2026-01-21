import os

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

utils_logger = Logger.get(service="ods_utils")


def is_ods_terminology_request(url: str) -> bool:
    """Check if the URL is for ODS Terminology API."""
    return "organisation-data-terminology-api" in url


def is_mock_testing_mode() -> bool:
    mock_testing_enabled = (
        os.environ.get("MOCK_TESTING_SCENARIOS", "").lower() == "true"
    )

    if not mock_testing_enabled:
        return False

    current_env = os.environ.get("ENVIRONMENT", "").lower()
    allowed_environments = ["dev", "test"]

    if current_env not in allowed_environments:
        error_msg = f"Mock testing scenarios cannot be enabled in environment '{current_env}'. Only allowed in: {', '.join(allowed_environments)}"
        utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_011, env=current_env)
        raise ValueError(error_msg)

    return True
