from functions.aws_url_builder import (
    build_cloudwatch_url,
    build_lambda_logs_url,
    build_lambda_metrics_url,
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
