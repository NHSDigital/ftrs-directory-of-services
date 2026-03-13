"""Build AWS console URLs for CloudWatch and Lambda resources."""

import os
import re
from typing import Any
from urllib.parse import quote


def build_cloudwatch_url(alarm_name: str, region: str | None = None) -> str:
    """
    Build CloudWatch console URL for the alarm.

    Args:
        alarm_name: CloudWatch alarm name
        region: AWS region (defaults to AWS_REGION env var or 'eu-west-2')

    Returns:
        str: CloudWatch console URL
    """
    region = region or os.environ.get("AWS_REGION", "eu-west-2")
    encoded_name = quote(alarm_name, safe="")
    return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#alarmsV2:alarm/{encoded_name}"


def build_lambda_logs_url(lambda_name: str, region: str | None = None) -> str:
    """
    Build CloudWatch Logs URL for Lambda function.

    Args:
        lambda_name: Lambda function name
        region: AWS region (defaults to AWS_REGION env var or 'eu-west-2')

    Returns:
        str: CloudWatch Logs console URL
    """
    region = region or os.environ.get("AWS_REGION", "eu-west-2")
    encoded_name = quote(lambda_name, safe="")
    return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/$252Faws$252Flambda$252F{encoded_name}"


def build_lambda_metrics_url(lambda_name: str, region: str | None = None) -> str:
    """
    Build Lambda metrics URL.

    Args:
        lambda_name: Lambda function name
        region: AWS region (defaults to AWS_REGION env var or 'eu-west-2')

    Returns:
        str: Lambda metrics console URL
    """
    region = region or os.environ.get("AWS_REGION", "eu-west-2")
    encoded_name = quote(lambda_name, safe="")
    return f"https://{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{encoded_name}?tab=monitoring"


def build_api_gateway_url(api_name: str, region: str | None = None) -> str:
    """Build API Gateway console URL."""
    region = region or os.environ.get("AWS_REGION", "eu-west-2")
    encoded_name = quote(api_name, safe="")
    return f"https://{region}.console.aws.amazon.com/apigateway/main/apis?region={region}&search={encoded_name}"


def build_waf_url(acl_name: str, region: str | None = None) -> str:
    """Build WAF console URL."""
    region = region or os.environ.get("AWS_REGION", "eu-west-2")
    encoded_name = quote(acl_name, safe="")
    return f"https://{region}.console.aws.amazon.com/wafv2/homev2/web-acls?region={region}&search={encoded_name}"


def build_cloudfront_url(distribution_id: str, region: str | None = None) -> str:
    """Build CloudFront console URL."""
    encoded_id = quote(distribution_id, safe="")
    return f"https://us-east-1.console.aws.amazon.com/cloudfront/v4/home?region=us-east-1#/distributions/{encoded_id}"


def extract_dimension_value(
    alarm_data: dict[str, Any], dimension_name: str
) -> str | None:
    """Find a dimension value by its name key in flattened alarm data."""
    pattern = re.compile(r"^Trigger_Dimensions_(\d+)_name$")
    for key, value in alarm_data.items():
        match = pattern.match(key)
        if match and value == dimension_name:
            return alarm_data.get(f"Trigger_Dimensions_{match.group(1)}_value")
    return None


def extract_region_code(alarm_arn: str) -> str:
    """
    Extract AWS region code from alarm ARN.

    Args:
        alarm_arn: CloudWatch alarm ARN

    Returns:
        str: AWS region code (e.g., 'eu-west-2')
    """
    arn_region_index = 3
    default_region = os.environ.get("AWS_REGION", "eu-west-2")
    try:
        parts = alarm_arn.split(":")
        return (
            parts[arn_region_index] if len(parts) > arn_region_index else default_region
        )
    except (IndexError, AttributeError):
        return default_region
