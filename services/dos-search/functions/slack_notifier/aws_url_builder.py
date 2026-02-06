"""Build AWS console URLs for CloudWatch and Lambda resources."""

from urllib.parse import quote


def build_cloudwatch_url(alarm_name: str, region: str = "eu-west-2") -> str:
    """
    Build CloudWatch console URL for the alarm.

    Args:
        alarm_name: CloudWatch alarm name
        region: AWS region

    Returns:
        str: CloudWatch console URL
    """
    encoded_name = quote(alarm_name, safe="")
    return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#alarmsV2:alarm/{encoded_name}"


def build_lambda_logs_url(lambda_name: str, region: str = "eu-west-2") -> str:
    """
    Build CloudWatch Logs URL for Lambda function.

    Args:
        lambda_name: Lambda function name
        region: AWS region

    Returns:
        str: CloudWatch Logs console URL
    """
    encoded_name = quote(lambda_name, safe="")
    return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/$252Faws$252Flambda$252F{encoded_name}"


def build_lambda_metrics_url(lambda_name: str, region: str = "eu-west-2") -> str:
    """
    Build Lambda metrics URL.

    Args:
        lambda_name: Lambda function name
        region: AWS region

    Returns:
        str: Lambda metrics console URL
    """
    encoded_name = quote(lambda_name, safe="")
    return f"https://{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{encoded_name}?tab=monitoring"


def extract_region_code(alarm_arn: str) -> str:
    """
    Extract AWS region code from alarm ARN.

    Args:
        alarm_arn: CloudWatch alarm ARN

    Returns:
        str: AWS region code (e.g., 'eu-west-2')
    """
    arn_region_index = 3
    default_region = "eu-west-2"
    try:
        parts = alarm_arn.split(":")
        return (
            parts[arn_region_index] if len(parts) > arn_region_index else default_region
        )
    except (IndexError, AttributeError):
        return default_region
