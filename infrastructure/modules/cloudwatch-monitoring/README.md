# CloudWatch Monitoring Module

Creates CloudWatch alarms and SNS notifications for AWS resources using predefined templates.

## How It Works

1. Choose a template (`lambda/config`, `api-gateway/config`, or `waf/config`)
2. Specify which resources to monitor with `monitored_resources`
3. Add metadata (API path, service name) with `resource_metadata`
4. Set threshold values, evaluation periods, and periods for each alarm
5. Module creates alarms with tags and SNS topic automatically
6. Subscribe the slack-notifier Lambda to the SNS topic for Slack notifications

## Usage

### Step 1: Create Monitoring Module

In your stack (e.g., `stacks/my_service/monitoring.tf`):

```hcl
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix   = local.resource_prefix
  sns_topic_name    = local.alarms_topic_name
  sns_display_name  = "My Service Lambda Alarms"
  kms_key_id        = data.aws_kms_key.sns_kms_key.arn
  alarm_config_path = "lambda/config"

  # Enable Slack notifications
  slack_notifier_enabled       = true
  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  monitored_resources = {
    my_lambda = module.my_lambda.lambda_function_name
  }

  resource_metadata = {
    my_lambda = {
      api_path = "/my-endpoint"
      service  = "My Service"
    }
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
    Name = local.alarms_topic_name
  }
}
```

### Step 2: Slack Notifications (Optional)

Slack notifications are now handled automatically by the module when you set:
- `slack_notifier_enabled = true`
- `slack_notifier_function_name = "your-slack-notifier-lambda-name"`

No separate `slack_notifications.tf` file is needed!

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

Placeholder - will be implemented in future tickets - FTRS-2230

### waf/config

Placeholder - will be implemented in future tickets - FTRS-2230

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
> Use variables for threshold, evaluation period, and period values instead of hard-coding them. This allows for environment-specific configuration and easier maintenance.

## Module Inputs

| Name | Required | Description |
|------|----------|-------------|
| `resource_prefix` | Yes | Prefix for alarm names |
| `sns_topic_name` | Yes | Name of SNS topic |
| `sns_display_name` | Yes | Display name for SNS topic |
| `alarm_config_path` | Yes | Template path (e.g., `lambda/config`) |
| `monitored_resources` | No | Map of resource keys to identifiers (default: `{}`) |
| `resource_metadata` | No | Map of resource keys to metadata (`api_path`, `service`) for alarm tags (default: `{}`) |
| `alarm_thresholds` | Yes | Map of resource keys to alarm thresholds |
| `alarm_evaluation_periods` | Yes | Map of resource keys to evaluation periods |
| `alarm_periods` | Yes | Map of resource keys to periods in seconds |
| `kms_key_id` | Yes | KMS key for SNS encryption |
| `enable_warning_alarms` | No | Enable warning alarms (default: `true`) |
| `slack_notifier_enabled` | No | Enable Slack notifier subscription (default: `false`) |
| `slack_notifier_function_name` | No | Name of Slack notifier Lambda function (required if `slack_notifier_enabled = true`) |
| `tags` | No | Tags for SNS topic (default: `{}`) |

## Module Outputs

| Name | Description |
|------|-------------|
| `sns_topic_arn` | ARN of the SNS topic (use for slack-notifier subscription) |
| `sns_topic_name` | Name of the SNS topic |
| `alarm_arns` | Map of alarm names to ARNs |
