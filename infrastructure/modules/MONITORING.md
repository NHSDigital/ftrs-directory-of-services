# Complete CloudWatch Monitoring Solution

This directory contains two complementary modules that provide a complete monitoring and alerting solution for AWS resources.

## Modules Overview

### 1. [cloudwatch-monitoring](./cloudwatch-monitoring/)

Creates CloudWatch alarms and SNS topic for AWS resource monitoring.

**Supported Resources:**

- Lambda functions
- API Gateway (REST and HTTP APIs)
- WAF WebACLs

**Features:**

- Built-in alarm templates for each resource type
- Custom alarm configurations
- Multiple resource support
- Warning and critical severity levels

### 2. [slack-notifications](./slack-notifications/)

Sends CloudWatch alarm notifications to Slack via Lambda.

**Features:**

- Automatic SNS subscription
- VPC support
- Configurable Lambda settings
- X-Ray tracing

## Complete Setup Example

```hcl
# Step 1: Create monitoring with alarms for multiple resources
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-service-alarms-prod"
  sns_display_name = "My Service Alarms"
  
  # Custom config with Lambda + API Gateway + WAF
  alarm_config_path = "${path.module}/alarms/multi-resource.json"
  
  monitored_resources = {
    api_lambda = module.api_lambda.lambda_function_name
    api        = module.api_gateway.api_name
    waf        = aws_wafv2_web_acl.main.name
  }
  
  alarm_thresholds = {
    api_lambda = {
      "duration-p99-critical" = 3000
      "errors-critical"       = 5
    }
    api = {
      "5xx-errors-critical"  = 10
      "latency-p99-critical" = 5000
    }
    waf = {
      "blocked-requests-critical" = 5000
    }
  }
  
  # ... evaluation periods and periods
}

# Step 2: Add Slack notifications
module "slack_notifications" {
  source = "../../modules/slack-notifications"

  resource_prefix = "my-service"
  sns_topic_arn   = module.monitoring.sns_topic_arn
  
  slack_webhook_url = var.slack_webhook_url
  environment       = "production"
  project_name      = "my-service"
  workspace         = terraform.workspace
  
  lambda_module_source = "../../modules/lambda"
  lambda_s3_bucket     = "my-artifacts-bucket"
  lambda_s3_key        = "lambda/slack-notifications.zip"
  
  subnet_ids         = data.aws_subnets.private.ids
  security_group_ids = [aws_security_group.lambda.id]
  
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = "myorg"
  aws_region     = "eu-west-2"
  vpc_id         = data.aws_vpc.main.id
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Resources                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Lambda Function│  │ API Gateway  │  │  WAF WebACL  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│         CloudWatch Alarms (cloudwatch-monitoring)            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Duration │  │  Errors  │  │ 5XX Errors│  │ Blocked  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬──────┘   │
│       └─────────────┼─────────────┼─────────────┘           │
└─────────────────────┼─────────────┼─────────────────────────┘
                      │             │
                      ▼             ▼
              ┌───────────────────────┐
              │      SNS Topic        │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  SNS Subscription     │
              └───────────┬───────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│         Slack Notification Lambda (slack-notifications)      │
│  ┌────────────────────────────────────────────────────┐     │
│  │  • Receives SNS messages                           │     │
│  │  • Parses CloudWatch alarm JSON                    │     │
│  │  • Formats message                                 │     │
│  │  • Sends to Slack webhook                          │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  Slack Channel│
                  └───────────────┘
```

## Quick Start Guide

### 1. Choose Your Monitoring Level

| Level | Use Case | Alarms |
|-------|----------|--------|
| **minimal** | Development, low-traffic | Errors, Throttles |
| **standard** | Production (recommended) | Duration, Errors, Throttles, Concurrency |
| **comprehensive** | High-criticality services | All metrics + Warning levels |

### 2. Deploy Monitoring

```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan

# Apply
terraform apply
```

### 3. Test Notifications

Trigger a test alarm to verify Slack integration:

```bash
aws cloudwatch set-alarm-state \
  --alarm-name "my-service-api-lambda-errors-critical" \
  --state-value ALARM \
  --state-reason "Testing Slack notifications"
```

## Configuration Options

### Monitoring Templates by Resource Type

**Lambda:**

- **lambda/minimal**: 2 alarms (Errors, Throttles)
- **lambda/standard**: 4 alarms (Duration p99, Errors, Throttles, Concurrency)
- **lambda/comprehensive**: 8 alarms (All metrics with Warning + Critical)

**API Gateway:**

- **api-gateway/minimal**: 2 alarms (5XX errors, Latency)
- **api-gateway/standard**: 4 alarms (4XX/5XX errors, Latency, Request spike)

**WAF:**

- **waf/minimal**: 2 alarms (Blocked requests, Allowed spike)
- **waf/standard**: 4 alarms (Blocked/Counted requests, Allowed spike)

### Custom Configurations

Create your own alarm configuration:

```json
{
  "my_lambda": [
    {
      "metric_name": "CustomMetric",
      "statistic": "Sum",
      "comparison_operator": "GreaterThanThreshold",
      "alarm_suffix": "custom-critical",
      "description": "Custom alarm description",
      "severity": "critical"
    }
  ]
}
```

## Best Practices

### 1. Alarm Thresholds

- Start with conservative thresholds
- Adjust based on actual metrics
- Use warning alarms for early detection

### 2. Evaluation Periods

- Critical alarms: 1-2 periods (fast response)
- Warning alarms: 2-3 periods (reduce noise)

### 3. SNS Topic

- One topic per service/environment
- Use descriptive names
- Enable encryption with KMS

### 4. Slack Notifications

- Use dedicated channels for different severity levels
- Configure VPC endpoints for private subnets
- Store webhook URLs in Secrets Manager

### 5. Cost Optimization

- Use minimal template for non-critical services
- Set appropriate CloudWatch Logs retention
- Monitor Lambda invocation costs

## Troubleshooting

### Alarms Not Triggering

1. Check alarm state: `aws cloudwatch describe-alarms`
2. Verify Lambda metrics: CloudWatch Console
3. Check evaluation periods and thresholds

### Slack Notifications Not Received

1. Verify SNS subscription: `aws sns list-subscriptions`
2. Check Lambda logs: CloudWatch Logs
3. Test webhook URL manually
4. Verify VPC configuration (if applicable)

### High Costs

1. Review alarm count and evaluation frequency
2. Check CloudWatch Logs retention
3. Optimize Lambda memory/timeout
4. Consider using minimal template

## Migration from Embedded Configuration

See [MIGRATION.md](./MIGRATION.md) for step-by-step migration guide from embedded alarm configurations to this module.

## Support

- **CloudWatch Monitoring**: [cloudwatch-monitoring/README.md](./cloudwatch-monitoring/README.md)
- **Slack Notifications**: [slack-notifications/README.md](./slack-notifications/README.md)
- **Examples**: 
  - [cloudwatch-monitoring/EXAMPLES.md](./cloudwatch-monitoring/EXAMPLES.md)
  - [slack-notifications/EXAMPLES.md](./slack-notifications/EXAMPLES.md)

## Contributing

When adding new features:

1. Update module documentation
2. Add examples
3. Test with multiple configurations
4. Update this overview document
