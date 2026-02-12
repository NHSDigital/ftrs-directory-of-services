# CloudWatch Monitoring & Slack Notifications

Reusable Terraform modules and stacks for AWS resource monitoring with CloudWatch alarms and Slack notifications.

## Overview

This solution provides:
- **CloudWatch alarms** for Lambda, API Gateway, and WAF
- **Slack notifications** for alarm events
- **Built-in templates** for quick adoption
- **Reusable modules** following DRY principles

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Stack (e.g., dos_search)             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  CloudWatch Monitoring                                 │ │
│  │  Module: cloudwatch-monitoring                         │ │
│  │  - Lambda/API Gateway/WAF alarms                       │ │
│  │  - SNS topic for notifications                         │ │
│  └────────────────────────────┬───────────────────────────┘ │
│                               │                              │
│  ┌────────────────────────────▼───────────────────────────┐ │
│  │  Slack Notifications (optional)                        │ │
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

## Quick Start

### Step 1: Add CloudWatch Monitoring

```hcl
# In your stack (e.g., infrastructure/stacks/my_service/monitoring.tf)
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = local.resource_prefix
  workspace_suffix = local.workspace_suffix
  
  sns_topic_name   = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}"
  sns_display_name = "My Service Lambda Alarms"
  
  # Use built-in template
  alarm_config_path = "lambda/standard"
  
  monitored_resources = {
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

### Step 2: Add Slack Notifications (Optional)

```hcl
# In your stack (e.g., infrastructure/stacks/my_service/slack_notifications.tf)
module "slack_notifier" {
  count  = var.enable_slack_notifications ? 1 : 0
  source = "../slack_notifier"

  environment = var.environment
  project     = var.project
  aws_region  = var.aws_region

  sns_topic_arn     = module.lambda_monitoring.sns_topic_arn
  slack_webhook_url = var.slack_webhook_url

  vpc_name                       = "${local.account_prefix}-vpc"
  security_group_ids             = [aws_security_group.lambda.id]
  artefacts_bucket_name          = local.artefacts_bucket
  lambda_artifact_key            = "lambda/slack-notifications.zip"
  lambda_runtime                 = "python3.11"
  cloudwatch_logs_retention_days = 7
}
```

### Step 3: Enable in Variables

```hcl
# In your terraform.tfvars
enable_slack_notifications = true
slack_webhook_url          = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

## Available Templates

### Lambda Monitoring

| Template | Alarms | Use Case |
|----------|--------|----------|
| `lambda/minimal` | Errors, Throttles | Basic monitoring |
| `lambda/standard` | Duration p99, Errors, Throttles, Concurrency | Recommended |
| `lambda/comprehensive` | All metrics + Warning levels | High-criticality |

### API Gateway Monitoring

| Template | Alarms | Use Case |
|----------|--------|----------|
| `api-gateway/minimal` | 5XX errors, Latency | Basic API monitoring |
| `api-gateway/standard` | 4XX/5XX errors, Latency, Request spike | Production APIs |

### WAF Monitoring

| Template | Alarms | Use Case |
|----------|--------|----------|
| `waf/minimal` | Blocked requests, Allowed spike | Basic WAF monitoring |
| `waf/standard` | Blocked/Counted requests, Allowed spike | Production WAF |

## Modules

### cloudwatch-monitoring

**Location**: `infrastructure/modules/cloudwatch-monitoring/`

**Purpose**: Creates CloudWatch alarms and SNS topic for AWS resources

**Supports**:
- Lambda functions
- API Gateway (REST/HTTP)
- WAF WebACLs

**Key Features**:
- Built-in templates for common patterns
- Custom configuration support
- Multiple resource monitoring
- Warning/Critical severity levels

**Documentation**: [cloudwatch-monitoring/README.md](./modules/cloudwatch-monitoring/README.md)

### slack-notifications

**Location**: `infrastructure/modules/slack-notifications/`

**Purpose**: Lambda function that sends CloudWatch alarms to Slack

**Key Features**:
- Resource-agnostic (works with any SNS topic)
- VPC support
- Configurable Lambda settings
- X-Ray tracing

**Documentation**: [slack-notifications/README.md](./modules/slack-notifications/README.md)

## Stacks

### slack_notifier

**Location**: `infrastructure/stacks/slack_notifier/`

**Purpose**: Standalone deployable stack for Slack notifications

**Use Cases**:
- Subscribe to multiple SNS topics from different stacks
- Centralized notification management
- Independent deployment lifecycle

**Documentation**: [slack_notifier/README.md](./stacks/slack_notifier/README.md)

## Examples

### Example 1: Lambda Monitoring Only

```hcl
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  alarm_config_path = "lambda/minimal"
  
  monitored_resources = {
    lambda = module.my_lambda.lambda_function_name
  }
  
  # ... thresholds, periods, etc.
}
```

### Example 2: Multi-Resource Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  alarm_config_path = "${path.module}/custom-config.json"
  
  monitored_resources = {
    api_lambda = module.api_lambda.lambda_function_name
    api        = module.api_gateway.api_name
    waf        = aws_wafv2_web_acl.main.name
  }
  
  # ... thresholds for all resources
}
```

### Example 3: With Slack Notifications

```hcl
# Monitoring
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"
  # ... configuration
}

# Slack notifications
module "slack_notifier" {
  source = "../slack_notifier"
  
  sns_topic_arn     = module.monitoring.sns_topic_arn
  slack_webhook_url = var.slack_webhook_url
  # ... configuration
}
```

## Configuration

### Required Variables

**For cloudwatch-monitoring**:
- `resource_prefix` - Prefix for alarm names
- `workspace_suffix` - Workspace suffix
- `sns_topic_name` - SNS topic name
- `sns_display_name` - SNS display name
- `monitored_resources` - Map of resources to monitor
- `alarm_thresholds` - Threshold values
- `alarm_evaluation_periods` - Evaluation periods
- `alarm_periods` - Period in seconds

**For slack-notifications**:
- `sns_topic_arn` - SNS topic to subscribe to
- `slack_webhook_url` - Slack webhook URL
- `environment` - Environment name
- `project` - Project name
- `aws_region` - AWS region
- `vpc_name` - VPC name
- `security_group_ids` - Security groups
- `artefacts_bucket_name` - S3 bucket for Lambda code
- `lambda_artifact_key` - S3 key for Lambda package

### Optional Variables

- `alarm_config_path` - Template or custom config path (default: "lambda/standard")
- `enable_warning_alarms` - Enable warning level alarms (default: true)
- `kms_key_id` - KMS key for SNS encryption
- `lambda_runtime` - Lambda runtime (default: "python3.11")
- `lambda_timeout` - Lambda timeout (default: 30)
- `lambda_memory_size` - Lambda memory (default: 128)
- `cloudwatch_logs_retention_days` - Log retention (default: 7)

## Testing

### Test Alarm Trigger

```bash
aws cloudwatch set-alarm-state \
  --alarm-name "my-service-api-lambda-errors-critical" \
  --state-value ALARM \
  --state-reason "Testing Slack notifications"
```

### Check Lambda Logs

```bash
aws logs tail /aws/lambda/my-service-slack-notifier-slack-notification --follow
```

### Verify SNS Subscription

```bash
aws sns list-subscriptions-by-topic \
  --topic-arn "arn:aws:sns:region:account:topic-name"
```

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
3. Test webhook URL manually
4. Verify VPC configuration (if applicable)
5. Check Lambda permissions

### High Costs

1. Review alarm count
2. Check evaluation frequency
3. Optimize CloudWatch Logs retention
4. Consider using minimal templates for non-critical services

## Migration Guide

See [cloudwatch-monitoring/MIGRATION.md](./modules/cloudwatch-monitoring/MIGRATION.md) for migrating from embedded alarm configurations.

## Support

- **CloudWatch Monitoring**: [modules/cloudwatch-monitoring/](./modules/cloudwatch-monitoring/)
- **Slack Notifications**: [modules/slack-notifications/](./modules/slack-notifications/)
- **Slack Notifier Stack**: [stacks/slack_notifier/](./stacks/slack_notifier/)

## Contributing

When adding new features:
1. Update module documentation
2. Add examples
3. Test with multiple configurations
4. Update this README
