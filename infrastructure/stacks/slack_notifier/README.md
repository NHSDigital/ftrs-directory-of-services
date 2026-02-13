# CloudWatch Monitoring & Slack Notifications

**Pre-configured monitoring infrastructure for service teams.** Everything is already set up - just use the modules, pick a template, and enable via `.tfvars`.

## What's Already Configured

- **Reusable Terraform modules** - Drop into your stack
- **Alarm templates** - Lambda, API Gateway, WAF patterns ready to use
- **Slack integration** - Centralised notification handler deployed
- **SNS topics** - Automatically created per service

**Your job**: Define which resources to monitor and enable notifications in your `.tfvars`

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                Your Stack (e.g., dos_search)                │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  CloudWatch Monitoring                                 │ │
│  │  Module: cloudwatch-monitoring                         │ │
│  │  - Lambda/API Gateway/WAF alarms                       │ │
│  │  - SNS topic for notifications                         │ │
│  └────────────────────────────┬───────────────────────────┘ │
│                               │                             │
│  ┌────────────────────────────▼───────────────────────────┐ │
│  │  Slack Notifications                                   │ │
│  │  Module: slack-notifications                           │ │
│  │  - Lambda function                                     │ │
│  │  - SNS subscription                                    │ │
│  │  - Formats and sends to Slack                          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
                          Slack Channel
```

## Quick Start (3 Steps)

### Step 1: Use the Module + Pick a Template

Add to your stack's `monitoring.tf` using a **pre-built template**:

```bash
# In your stack (e.g., infrastructure/stacks/my_service/monitoring.tf)
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = local.resource_prefix
  workspace_suffix = local.workspace_suffix

  sns_topic_name   = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}"
  sns_display_name = "My Service Lambda Alarms"

  # Use pre-built template (no custom config needed!)
  alarm_config_path = "comprehensive"

  lambda_functions = {
    api_lambda = module.api_lambda.lambda_function_name
  }

  alarm_thresholds = {
    api_lambda = {
      "duration-p99-critical"          = 3000
      "errors-critical"                = 5
      "throttles-critical"             = 0
      "concurrent-executions-critical" = 100
    }
  }

  alarm_evaluation_periods = {
    api_lambda = {
      "duration-p99-critical"          = 2
      "errors-critical"                = 2
      "throttles-critical"             = 1
      "concurrent-executions-critical" = 2
    }
  }

  alarm_periods = {
    api_lambda = {
      "duration-p99-critical"          = 300
      "errors-critical"                = 300
      "throttles-critical"             = 60
      "concurrent-executions-critical" = 300
    }
  }
}
```

### Step 2: Define Slack Integration

Add to your stack's `slack_notifications.tf` (references centralised slack_notifier):

```bash
# In your stack (e.g., infrastructure/stacks/my_service/slack_notifications.tf)
data "aws_lambda_function" "slack_notifier" {
  count         = var.enable_slack_notifications ? 1 : 0
  function_name = "${local.project_prefix}-slack-notifier${local.workspace_suffix}"
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  count         = var.enable_slack_notifications ? 1 : 0
  statement_id  = "AllowExecutionFromSNS-${local.resource_prefix}"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_notifier[0].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.lambda_monitoring.sns_topic_arn
}

resource "aws_sns_topic_subscription" "lambda_alarms_to_slack" {
  count     = var.enable_slack_notifications ? 1 : 0
  topic_arn = module.lambda_monitoring.sns_topic_arn
  protocol  = "lambda"
  endpoint  = data.aws_lambda_function.slack_notifier[0].arn

  depends_on = [aws_lambda_permission.allow_sns_invoke]
}
```

### Step 3: Enable via .tfvars

Add the variable definition:

```text
# In your stack variables.tf
variable "enable_slack_notifications" {
  description = "Enable Slack notifications for CloudWatch alarms"
  type        = bool
  default     = false
}
```

```text
# In your environment tfvars (e.g., environments/prod/my_service.tfvars)
enable_slack_notifications = true
```

**That's it!** Alarms are created and Slack notifications flow automatically.

## Available Templates

| Template | Alarms | Use Case |
|----------|--------|----------|
| `minimal` | Errors, Throttles | Basic monitoring |
| `standard` | Duration p99, Errors, Throttles, Concurrency | Recommended |
| `comprehensive` | All metrics + Warning levels | High-criticality |
| Custom path | Your own config | `${path.module}/custom-config.json` |

## Examples

### Example 1: Lambda Monitoring Only

```shell
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  alarm_config_path = "minimal"

  lambda_functions = {
    lambda = module.my_lambda.lambda_function_name
  }

  # ... thresholds, periods, etc.
}
```

### Example 2: Multi-Resource Monitoring

```shell
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  alarm_config_path = "${path.module}/custom-config.json"

  lambda_functions = {
    api_lambda = module.api_lambda.lambda_function_name
  }

  # ... thresholds for all resources
}
```

### Example 3: With Slack Notifications

```text
# Monitoring
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"
  # ... configuration
}

# Slack notifications via Lambda data source
data "aws_lambda_function" "slack_notifier" {
  count         = var.enable_slack_notifications ? 1 : 0
  function_name = "${local.project_prefix}-slack-notifier${local.workspace_suffix}"
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  count         = var.enable_slack_notifications ? 1 : 0
  statement_id  = "AllowExecutionFromSNS-${local.resource_prefix}"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_notifier[0].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.monitoring.sns_topic_arn
}

resource "aws_sns_topic_subscription" "alarms_to_slack" {
  count      = var.enable_slack_notifications ? 1 : 0
  topic_arn  = module.monitoring.sns_topic_arn
  protocol   = "lambda"
  endpoint   = data.aws_lambda_function.slack_notifier[0].arn
  depends_on = [aws_lambda_permission.allow_sns_invoke]
}
```

## Configuration Reference

### Enabling Slack Notifications

**Per-environment control** via `.tfvars` files:

```text
# infrastructure/environments/{env}/{stack_name}.tfvars
enable_slack_notifications = true
```

**Example - dos_search stack:**

- Enabled: `dev`, `int`
- Disabled: `ref`, `prod`

**Prerequisites:**

- `slack_notifier` stack deployed (already done centrally)
- Webhook configured via GitHub secrets (already done)
- Alarms always created; Slack is optional per environment

### Filtering Alarms by Resource

To apply alarms to specific resources only, add `resource_type_filter` to your monitoring module:

```text
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  # Only apply alarms to specific resources
  resource_type_filter = ["api_lambda"]  # Only api_lambda gets alarms

  lambda_functions = {
    api_lambda    = module.api_lambda.lambda_function_name
    worker_lambda = module.worker_lambda.lambda_function_name
  }

  # ... rest of configuration
}
```

**Default**: `null` (all resources get alarms)

### Minimal Required Configuration

**For cloudwatch-monitoring module**:

- `resource_prefix` - Prefix for alarm names
- `workspace_suffix` - Workspace suffix
- `sns_topic_name` - SNS topic name
- `sns_display_name` - SNS display name
- `monitored_resources` - Map of resources to monitor
- `alarm_thresholds` - Threshold values
- `alarm_evaluation_periods` - Evaluation periods
- `alarm_periods` - Period in seconds

**For slack-notifications**:

- Service teams don't configure this directly
- The `slack_notifier` stack is deployed and maintained centrally
- Reference it via `aws_lambda_function` data source (see Quick Start)

**Note**: Slack webhook URL is configured via GitHub environment secrets (`SLACK_WEBHOOK_ALARMS_URL`) and deployed through the centralized `slack_notifier` stack.

### Optional Variables

- `alarm_config_path` - Template or custom config path (default: "lambda/standard")
- `enable_warning_alarms` - Enable warning level alarms (default: true)
- `kms_key_id` - KMS key for SNS encryption

## Testing

See the [alarm templates documentation](../../modules/cloudwatch-monitoring/templates/README.md) for testing alarm configurations and make targets.

## Best Practices

1. **Start with templates**: Use built-in templates before creating custom configs
2. **Adjust thresholds**: Tune based on actual service behavior
3. **Use warning alarms**: Enable early detection of issues
4. **Separate concerns**: Use slack_notifier stack for centralized notifications
5. **Test thoroughly**: Trigger test alarms before production deployment
6. **Monitor costs**: Review alarm count and evaluation frequency
7. **Document thresholds**: Keep track of why specific values were chosen

## Troubleshooting

### Alarms Not Triggering

1. Check alarm state: `aws cloudwatch describe-alarms`
2. Verify metrics are being published
3. Check evaluation periods and thresholds
4. Review alarm configuration

### Slack Notifications Not Received

1. Verify SNS subscription exists
2. Check Lambda logs for errors
3. Verify `slack_notifier` stack is deployed
4. Check GitHub environment secret `SLACK_WEBHOOK_ALARMS_URL` is configured
5. Verify VPC configuration (if applicable)
6. Check Lambda permissions

## Support

- **CloudWatch Monitoring Module**: [modules/cloudwatch-monitoring/](../../modules/cloudwatch-monitoring/)
- **Alarm Templates**: [modules/cloudwatch-monitoring/templates/](../../modules/cloudwatch-monitoring/templates/)
- **Centralized Slack Handler**: Deployed via `slack_notifier` stack (this directory)

## Contributing

When adding new features:

1. Update module documentation
2. Add examples
3. Test with multiple configurations
4. Update this README
