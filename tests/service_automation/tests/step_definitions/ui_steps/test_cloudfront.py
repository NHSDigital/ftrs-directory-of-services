
import pytest
import allure
from step_definitions.common_steps.setup_steps import *
from utilities.infra.cloudfront_util import CloudFrontWrapper
from utilities.common.resource_name import get_resource_name
from loguru import logger

@pytest.mark.test
def test_get_cloudfront(workspace, project, env,):
    cloudfront_s3 = get_resource_name(project, workspace, env, "read-only-viewer", "frontend-bucket")
    logger.info(f"CloudFront S3 Bucket: {cloudfront_s3}")
    cfw = CloudFrontWrapper()
    cloudfront_url = cfw.list_distributions(cloudfront_s3)
    logger.info(f"CloudFront Distributions: {cloudfront_url}")


