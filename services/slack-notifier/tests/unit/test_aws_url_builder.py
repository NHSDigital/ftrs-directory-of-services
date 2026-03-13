from functions.aws_url_builder import (
    build_api_gateway_url,
    build_cloudfront_url,
    build_cloudwatch_url,
    build_lambda_logs_url,
    build_lambda_metrics_url,
    build_waf_url,
    extract_dimension_value,
    extract_region_code,
)


class TestBuildCloudwatchUrl:
    def test_default_region(self):
        url = build_cloudwatch_url("test-alarm")
        assert (
            url
            == "https://eu-west-2.console.aws.amazon.com/cloudwatch/home?region=eu-west-2#alarmsV2:alarm/test-alarm"
        )

    def test_custom_region(self):
        url = build_cloudwatch_url("test-alarm", "us-east-1")
        assert (
            url
            == "https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/test-alarm"
        )

    def test_url_encoding(self):
        url = build_cloudwatch_url("test alarm with spaces")
        assert "test%20alarm%20with%20spaces" in url


class TestBuildLambdaLogsUrl:
    def test_default_region(self):
        url = build_lambda_logs_url("test-function")
        assert (
            url
            == "https://eu-west-2.console.aws.amazon.com/cloudwatch/home?region=eu-west-2#logsV2:log-groups/log-group/$252Faws$252Flambda$252Ftest-function"
        )

    def test_custom_region(self):
        url = build_lambda_logs_url("test-function", "us-west-2")
        assert (
            url
            == "https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#logsV2:log-groups/log-group/$252Faws$252Flambda$252Ftest-function"
        )


class TestBuildLambdaMetricsUrl:
    def test_default_region(self):
        url = build_lambda_metrics_url("test-function")
        assert (
            url
            == "https://eu-west-2.console.aws.amazon.com/lambda/home?region=eu-west-2#/functions/test-function?tab=monitoring"
        )

    def test_custom_region(self):
        url = build_lambda_metrics_url("test-function", "ap-south-1")
        assert (
            url
            == "https://ap-south-1.console.aws.amazon.com/lambda/home?region=ap-south-1#/functions/test-function?tab=monitoring"
        )


class TestExtractRegionCode:
    def test_valid_arn(self):
        arn = "arn:aws:cloudwatch:us-east-1:000000000000:alarm:test-alarm"  # gitleaks:allow
        result = extract_region_code(arn)
        assert result == "us-east-1"

    def test_short_arn(self):
        arn = "arn:aws:cloudwatch"
        result = extract_region_code(arn)
        assert result == "eu-west-2"

    def test_empty_arn(self):
        result = extract_region_code("")
        assert result == "eu-west-2"


class TestBuildApiGatewayUrl:
    def test_default_region(self):
        url = build_api_gateway_url("my-api")
        assert "eu-west-2.console.aws.amazon.com/apigateway" in url
        assert "my-api" in url

    def test_custom_region(self):
        url = build_api_gateway_url("my-api", "us-east-1")
        assert "us-east-1.console.aws.amazon.com/apigateway" in url

    def test_url_encoding(self):
        url = build_api_gateway_url("my api")
        assert "my%20api" in url


class TestBuildWafUrl:
    def test_default_region(self):
        url = build_waf_url("my-acl")
        assert "eu-west-2.console.aws.amazon.com/wafv2" in url
        assert "my-acl" in url

    def test_custom_region(self):
        url = build_waf_url("my-acl", "us-east-1")
        assert "us-east-1.console.aws.amazon.com/wafv2" in url


class TestBuildCloudfrontUrl:
    def test_distribution_id_in_url(self):
        url = build_cloudfront_url("EDFDVBD6EXAMPLE")
        assert "EDFDVBD6EXAMPLE" in url
        assert "cloudfront" in url

    def test_always_us_east_1(self):
        url = build_cloudfront_url("EDFDVBD6EXAMPLE", "eu-west-2")
        assert "us-east-1.console.aws.amazon.com" in url


class TestExtractDimensionValue:
    def test_finds_by_name(self):
        alarm_data = {
            "Trigger_Dimensions_0_name": "FunctionName",
            "Trigger_Dimensions_0_value": "my-lambda",
        }
        assert extract_dimension_value(alarm_data, "FunctionName") == "my-lambda"

    def test_finds_second_dimension(self):
        alarm_data = {
            "Trigger_Dimensions_0_name": "WebACL",
            "Trigger_Dimensions_0_value": "my-acl",
            "Trigger_Dimensions_1_name": "Rule",
            "Trigger_Dimensions_1_value": "ALL",
        }
        assert extract_dimension_value(alarm_data, "Rule") == "ALL"

    def test_returns_none_when_not_found(self):
        alarm_data = {
            "Trigger_Dimensions_0_name": "FunctionName",
            "Trigger_Dimensions_0_value": "my-lambda",
        }
        assert extract_dimension_value(alarm_data, "WebACL") is None

    def test_empty_data(self):
        assert extract_dimension_value({}, "FunctionName") is None
