# CloudWatch Monitoring Module

Creates CloudWatch alarms and SNS notifications for AWS resources using predefined templates.

## How It Works

1. Choose a template (`lambda/config`, `api-gateway/config`, or `waf/config`)
2. Specify which resources to monitor
3. Set threshold values for each alarm
4. Module creates alarms and SNS topic automatically
5. Subscribe the slack-notifier Lambda to the SNS topic for Slack notifications

## Usage

### Step 1: Create Monitoring Module

In your stack (e.g., `stacks/my_service/monitoring.tf`):

```hcl
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix   = local.resource_prefix
  sns_topic_name    = "${local.resource_prefix}-lambda-alarms"
  sns_display_name  = "My Service Lambda Alarms"
  kms_key_id        = data.aws_kms_key.sqs_kms_key.arn
  alarm_config_path = "lambda/config"

  monitored_resources = {
    my_lambda = module.my_lambda.lambda_function_name
  }

  alarm_thresholds = {
    my_lambda = {
      "duration-p95-warning"           = var.lambda_duration_p95_warning_ms
      "duration-p99-critical"          = var.lambda_duration_p99_critical_ms
      "errors-warning"                 = var.lambda_errors_warning_threshold
      "errors-critical"                = var.lambda_errors_critical_threshold
      "throttles-critical"             = var.lambda_throttles_critical_threshold
      "concurrent-executions-warning"  = var.lambda_concurrent_executions_warning
      "concurrent-executions-critical" = var.lambda_concurrent_executions_critical
      "invocations-spike-critical"     = var.lambda_invocations_spike_critical
    }
  }

  alarm_evaluation_periods = {
    my_lambda = {
      "duration-p95-warning"           = var.lambda_alarm_evaluation_periods
      "duration-p99-critical"          = var.lambda_alarm_evaluation_periods
      "errors-warning"                 = var.lambda_alarm_evaluation_periods
      "errors-critical"                = var.lambda_alarm_evaluation_periods
      "throttles-critical"             = var.lambda_throttles_evaluation_periods
      "concurrent-executions-warning"  = var.lambda_alarm_evaluation_periods
      "concurrent-executions-critical" = var.lambda_alarm_evaluation_periods
      "invocations-spike-critical"     = var.lambda_alarm_evaluation_periods
    }
  }

  alarm_periods = {
    my_lambda = {
      "duration-p95-warning"           = var.lambda_alarm_period_seconds
      "duration-p99-critical"          = var.lambda_alarm_period_seconds
      "errors-warning"                 = var.lambda_alarm_period_seconds
      "errors-critical"                = var.lambda_alarm_period_seconds
      "throttles-critical"             = var.lambda_throttles_period_seconds
      "concurrent-executions-warning"  = var.lambda_alarm_period_seconds
      "concurrent-executions-critical" = var.lambda_alarm_period_seconds
      "invocations-spike-critical"     = var.invocations_spike_period_seconds
    }
  }

  enable_warning_alarms = var.enable_warning_alarms

  tags = {
    Name = "${local.resource_prefix}-lambda-alarms"
  }
}
```

### Step 2: Connect to Slack Notifier

In your stack (e.g., `stacks/my_service/slack_notifications.tf`):

```hcl
data "aws_lambda_function" "slack_notifier" {
  count         = var.slack_notifier_stack_enabled ? 1 : 0
  function_name = "${local.project_prefix}-slack-notifier"
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  count         = var.slack_notifier_stack_enabled ? 1 : 0
  statement_id  = "AllowExecutionFromSNS-${local.resource_prefix}"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_notifier[0].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.lambda_monitoring.sns_topic_arn
}

resource "aws_sns_topic_subscription" "lambda_alarms_to_slack" {
  count     = var.slack_notifier_stack_enabled ? 1 : 0
  topic_arn = module.lambda_monitoring.sns_topic_arn
  protocol  = "lambda"
  endpoint  = data.aws_lambda_function.slack_notifier[0].arn

  depends_on = [aws_lambda_permission.allow_sns_invoke]
}
```

## Available Templates

### lambda/config

Monitors Lambda functions with these alarms:

| Alarm Suffix | Metric | Statistic | Severity |
|--------------|--------|-----------|----------|
| `duration-p95-warning` | Duration | p95 | warning |
| `duration-p99-critical` | Duration | p99 | critical |
| `concurrent-executions-warning` | ConcurrentExecutions | Maximum | warning |
| `concurrent-executions-critical` | ConcurrentExecutions | Maximum | critical |
| `throttles-critical` | Throttles | Sum | critical |
| `invocations-spike-critical` | Invocations | Sum | critical |
| `errors-warning` | Errors | Sum | warning |
| `errors-critical` | Errors | Sum | critical |

### api-gateway/config

Placeholder - will be implemented in future tickets

### waf/config

Placeholder - will be implemented in future tickets

## Adding New Alarms to Templates

To add alarms to an existing template, edit the JSON file in `templates/`:

```json
{
  "lambda": [
    {
      "metric_name": "Errors",
      "statistic": "Sum",
      "comparison_operator": "GreaterThanThreshold",
      "alarm_suffix": "errors-critical",
      "description": "Lambda errors critical threshold",
      "severity": "critical"
    }
  ]
}
```

Then add corresponding thresholds, evaluation periods, and periods in your module call.

> [!NOTE]
> Use variables for threshold, evaluation period, and period values instead of hardcoding them. This allows for environment-specific configuration and easier maintenance.

## Module Inputs

| Name | Required | Description |
|------|----------|-------------|
| `resource_prefix` | Yes | Prefix for alarm names |
| `sns_topic_name` | Yes | Name of SNS topic |
| `sns_display_name` | Yes | Display name for SNS topic |
| `alarm_config_path` | Yes | Template path (e.g., `lambda/config`) |
| `monitored_resources` | No | Map of resource keys to identifiers (default: `{}`) |
| `alarm_thresholds` | Yes | Map of resource keys to alarm thresholds |
| `alarm_evaluation_periods` | Yes | Map of resource keys to evaluation periods |
| `alarm_periods` | Yes | Map of resource keys to periods in seconds |
| `kms_key_id` | Yes | KMS key for SNS encryption |
| `enable_warning_alarms` | No | Enable warning alarms (default: `true`) |
| `tags` | No | Tags for SNS topic (default: `{}`) |

## Module Outputs

| Name | Description |
|------|-------------|
| `sns_topic_arn` | ARN of the SNS topic (use for slack-notifier subscription) |
| `sns_topic_name` | Name of the SNS topic |
| `alarm_arns` | Map of alarm names to ARNs |
