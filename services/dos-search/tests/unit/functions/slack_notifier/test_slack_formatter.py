from functions.slack_notifier.slack_formatter import (
    build_slack_message,
    format_timestamp,
    get_severity_from_alarm_name,
)


class TestGetSeverityFromAlarmName:
    def test_warning_severity(self):
        assert (
            get_severity_from_alarm_name("test-lambda-duration-p95-warning")
            == "warning"
        )
        assert get_severity_from_alarm_name("search-lambda-errors-warning") == "warning"

    def test_critical_severity(self):
        assert (
            get_severity_from_alarm_name("test-lambda-duration-p99-critical")
            == "critical"
        )
        assert (
            get_severity_from_alarm_name("search-lambda-errors-critical") == "critical"
        )

    def test_unknown_severity(self):
        assert get_severity_from_alarm_name("test-alarm") == "unknown"
        assert get_severity_from_alarm_name("some-other-alarm") == "unknown"

    def test_case_insensitive(self):
        assert get_severity_from_alarm_name("TEST-LAMBDA-WARNING") == "warning"
        assert get_severity_from_alarm_name("TEST-LAMBDA-CRITICAL") == "critical"


class TestFormatTimestamp:
    def test_valid_timestamp(self):
        result = format_timestamp("2024-01-29T10:30:00+0000")
        assert "<!date^" in result
        assert "1706524200" in result

    def test_valid_timestamp_with_colon(self):
        result = format_timestamp("2024-01-29T10:30:00+00:00")
        assert "<!date^" in result

    def test_empty_timestamp(self):
        result = format_timestamp("")
        assert result == "Unknown"

    def test_invalid_timestamp(self):
        result = format_timestamp("invalid-date")
        assert result == "invalid-date"


class TestBuildSlackMessage:
    def test_alarm_state_message_critical(self):
        alarm_data = {
            "AlarmName": "test-lambda-errors-critical",
            "AlarmArn": "arn:aws:cloudwatch:eu-west-2:000000000000:alarm:test-alarm",  # gitleaks:allow
            "NewStateValue": "ALARM",
            "NewStateReason": "Threshold exceeded",
            "Trigger_Threshold": 100,
            "Trigger_Statistic": "Average",
            "Trigger_MetricName": "Errors",
            "Trigger_Period": 60,
            "Trigger_EvaluationPeriods": 2,
            "StateChangeTime": "2024-01-29T10:30:00+0000",
            "Trigger_Dimensions_0_value": "test-lambda",
            "Region": "EU (London)",
        }

        result = build_slack_message(alarm_data)

        assert result["text"] == "🚨 CloudWatch Alarm: CRITICAL"
        assert (
            result["blocks"][0]["text"]["text"]
            == "🚨 CRITICAL: test-lambda-errors-critical"
        )
        assert any("Errors" in str(block) for block in result["blocks"])
        assert any("100" in str(block) for block in result["blocks"])

    def test_alarm_state_message_warning(self):
        alarm_data = {
            "AlarmName": "test-lambda-duration-p95-warning",
            "AlarmArn": "arn:aws:cloudwatch:eu-west-2:000000000000:alarm:test-alarm",  # gitleaks:allow
            "NewStateValue": "ALARM",
            "NewStateReason": "Threshold exceeded",
            "Trigger_Threshold": 600,
            "Trigger_Statistic": "p95",
            "Trigger_MetricName": "Duration",
            "Trigger_Period": 60,
            "Trigger_EvaluationPeriods": 2,
            "StateChangeTime": "2024-01-29T10:30:00+0000",
            "Trigger_Dimensions_0_value": "test-lambda",
            "Region": "EU (London)",
        }

        result = build_slack_message(alarm_data)

        assert result["text"] == "⚠️ CloudWatch Alarm: WARNING"
        assert (
            result["blocks"][0]["text"]["text"]
            == "⚠️ WARNING: test-lambda-duration-p95-warning"
        )
        assert any("Duration" in str(block) for block in result["blocks"])
        assert any("600" in str(block) for block in result["blocks"])

    def test_ok_state_message(self):
        alarm_data = {
            "AlarmName": "test-alarm",
            "NewStateValue": "OK",
            "NewStateReason": "Back to normal",
            "Trigger_MetricName": "Errors",
            "Trigger_Statistic": "Sum",
            "Trigger_Threshold": 0,
            "Trigger_Period": 30,
            "Trigger_EvaluationPeriods": 1,
            "AlarmArn": "arn:aws:cloudwatch:eu-west-2:000000000000:alarm:test",  # gitleaks:allow
            "Trigger_Dimensions_0_value": "lambda-func",
        }

        result = build_slack_message(alarm_data)

        assert "✅" in result["text"]
        assert result["blocks"][0]["text"]["text"] == "✅ OK: test-alarm"

    def test_insufficient_data_state(self):
        alarm_data = {
            "AlarmName": "test-alarm",
            "NewStateValue": "INSUFFICIENT_DATA",
            "NewStateReason": "Not enough data",
            "Trigger_MetricName": "Invocations",
            "Trigger_Statistic": "Sum",
            "Trigger_Threshold": 10,
            "Trigger_Period": 300,
            "Trigger_EvaluationPeriods": 1,
            "AlarmArn": "",
            "Trigger_Dimensions_0_value": "my-lambda",
        }

        result = build_slack_message(alarm_data)

        assert "⚠️" in result["text"]

    def test_missing_optional_fields(self):
        alarm_data = {
            "AlarmName": "minimal-alarm-critical",
            "NewStateValue": "ALARM",
        }

        result = build_slack_message(alarm_data)

        assert result["text"] == "🚨 CloudWatch Alarm: CRITICAL"
        assert "minimal-alarm-critical" in result["blocks"][0]["text"]["text"]
        assert any("N/A" in str(block) for block in result["blocks"])

    def test_url_links_present(self):
        alarm_data = {
            "AlarmName": "test-alarm",
            "AlarmArn": "arn:aws:cloudwatch:us-east-1:000000000000:alarm:test",  # gitleaks:allow
            "NewStateValue": "ALARM",
            "Trigger_Dimensions_0_value": "my-function",
        }

        result = build_slack_message(alarm_data)

        links_section = next(
            b
            for b in result["blocks"]
            if b.get("type") == "section" and "View Alarm" in str(b)
        )
        assert "us-east-1.console.aws.amazon.com" in str(links_section)
        assert "Lambda Logs" in str(links_section)
        assert "Lambda Metrics" in str(links_section)

    def test_unknown_state_emoji(self):
        alarm_data = {
            "AlarmName": "test-alarm",
            "NewStateValue": "UNKNOWN_STATE",
        }
        result = build_slack_message(alarm_data)
        assert "📊" in result["text"]
