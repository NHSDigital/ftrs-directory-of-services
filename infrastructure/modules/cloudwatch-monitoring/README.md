# CloudWatch Monitoring Module

Reusable Terraform module for AWS resource monitoring with CloudWatch alarms and SNS notifications.

## Features

- Creates SNS topic for alarm notifications
- Configures CloudWatch alarms based on JSON configuration
- Supports multiple AWS resource types:
  - **Lambda functions**
  - **API Gateway** (REST and HTTP APIs)
  - **WAF WebACLs**
- Flexible threshold and evaluation period configuration
- Warning/Critical severity levels
- **Built-in templates** for common monitoring patterns
- Support for custom alarm configurations

## Quick Start with Templates

### Lambda Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-dev"
  
  sns_topic_name   = "my-service-alarms-dev"
  sns_display_name = "My Service Alarms"
  
  alarm_config_path = "lambda/minimal"  # Built-in Lambda template
  
  monitored_resources = {
    api_lambda = module.api_lambda.lambda_function_name
  }
  
  alarm_thresholds = {
    api_lambda = {
      "errors-critical"    = 5
      "throttles-critical" = 0
    }
  }
  
  alarm_evaluation_periods = {
    api_lambda = {
      "errors-critical"    = 2
      "throttles-critical" = 1
    }
  }
  
  alarm_periods = {
    api_lambda = {
      "errors-critical"    = 300
      "throttles-critical" = 60
    }
  }
}
```

### API Gateway Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-api"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-api-alarms-prod"
  sns_display_name = "My API Alarms"
  
  alarm_config_path = "api-gateway/standard"
  
  monitored_resources = {
    api = module.api_gateway.api_name
  }
  
  alarm_thresholds = {
    api = {
      "4xx-errors-warning"      = 100
      "5xx-errors-critical"     = 10
      "latency-p99-critical"    = 5000
      "request-spike-critical"  = 10000
    }
  }
  
  alarm_evaluation_periods = {
    api = {
      "4xx-errors-warning"      = 3
      "5xx-errors-critical"     = 2
      "latency-p99-critical"    = 2
      "request-spike-critical"  = 1
    }
  }
  
  alarm_periods = {
    api = {
      "4xx-errors-warning"      = 300
      "5xx-errors-critical"     = 300
      "latency-p99-critical"    = 300
      "request-spike-critical"  = 3600
    }
  }
}
```

### WAF Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-waf"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-waf-alarms-prod"
  sns_display_name = "My WAF Alarms"
  
  alarm_config_path = "waf/standard"
  
  monitored_resources = {
    waf = aws_wafv2_web_acl.main.name
  }
  
  alarm_thresholds = {
    waf = {
      "blocked-requests-warning"        = 1000
      "blocked-requests-critical"       = 5000
      "allowed-requests-spike-critical" = 50000
      "counted-requests-warning"        = 500
    }
  }
  
  alarm_evaluation_periods = {
    waf = {
      "blocked-requests-warning"        = 2
      "blocked-requests-critical"       = 2
      "allowed-requests-spike-critical" = 1
      "counted-requests-warning"        = 2
    }
  }
  
  alarm_periods = {
    waf = {
      "blocked-requests-warning"        = 300
      "blocked-requests-critical"       = 300
      "allowed-requests-spike-critical" = 3600
      "counted-requests-warning"        = 300
    }
  }
}
```

### Multi-Resource Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-service-alarms-prod"
  sns_display_name = "My Service Alarms"
  
  # Custom config with multiple resource types
  alarm_config_path = "${path.module}/alarms/multi-resource.json"
  
  monitored_resources = {
    api_lambda = module.api_lambda.lambda_function_name
    api        = module.api_gateway.api_name
    waf        = aws_wafv2_web_acl.main.name
  }
  
  # Define thresholds for all resources
  alarm_thresholds = {
    api_lambda = { ... }
    api        = { ... }
    waf        = { ... }
  }
  
  # ... evaluation periods and periods
}
```

## Custom Configuration

You can provide your own JSON configuration file:

```hcl
module "lambda_monitoring" {
  source = "../../modules/lambda-monitoring"

  alarm_config_path = "${path.module}/alarms/custom-config.json"
  
  # ... rest of configuration
}
```

## Available Templates

| Resource Type | Template | Metrics Monitored | Use Case |
|--------------|----------|------------------|----------|
| **Lambda** | lambda/minimal | Errors, Throttles | Basic monitoring |
| **Lambda** | lambda/standard | Duration, Errors, Throttles, Concurrency | Recommended |
| **Lambda** | lambda/comprehensive | All metrics + Warning levels | High-criticality |
| **API Gateway** | api-gateway/minimal | 5XX errors, Latency | Basic API monitoring |
| **API Gateway** | api-gateway/standard | 4XX/5XX errors, Latency, Request spike | Production APIs |
| **WAF** | waf/minimal | Blocked requests, Allowed spike | Basic WAF monitoring |
| **WAF** | waf/standard | Blocked/Counted requests, Allowed spike | Production WAF |

## JSON Configuration Format

```json
{
  "my_lambda": [
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

## Inputs

| Name | Description | Type | Required |
|------|-------------|------|----------|
| resource_prefix | Prefix for alarm names | string | yes |
| workspace_suffix | Workspace suffix for resource naming | string | yes |
| sns_topic_name | Name of the SNS topic | string | yes |
| sns_display_name | Display name for the SNS topic | string | yes |
| alarm_config_path | Path to JSON alarm configuration or template name (e.g., 'lambda/standard', 'api-gateway/minimal', 'waf/standard') | string | no (default: 'lambda/standard') |
| monitored_resources | Map of resource keys to their identifiers (Lambda names, API Gateway names, WAF WebACL names) | map(string) | yes |
| lambda_functions | (Deprecated: use monitored_resources) Map of lambda function keys to their names | map(string) | no |
| alarm_thresholds | Alarm thresholds by resource and alarm type | map(map(number)) | yes |
| alarm_evaluation_periods | Evaluation periods by resource and alarm type | map(map(number)) | yes |
| alarm_periods | Period in seconds by resource and alarm type | map(map(number)) | yes |
| kms_key_id | KMS key ID for SNS encryption | string | no |
| enable_warning_alarms | Enable warning level alarms | boolean | no |
| tags | Tags for SNS topic | map(string) | no |

## Outputs

| Name | Description |
|------|-------------|
| sns_topic_arn | ARN of the SNS topic |
| sns_topic_name | Name of the SNS topic |
| alarm_arns | Map of alarm names to ARNs |

## Integration with Slack Notifications

This module works seamlessly with the `slack-notifications` module:

```hcl
module "lambda_monitoring" {
  source = "../../modules/lambda-monitoring"
  # ... configuration
}

module "slack_notifications" {
  source = "../../modules/slack-notifications"
  
  sns_topic_arn = module.lambda_monitoring.sns_topic_arn
  # ... configuration
}
```

See the [slack-notifications module](../slack-notifications/README.md) for details.
