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

## Usage Examples

### Lambda Monitoring (Standard Template)

```hcl
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"

  sns_topic_name   = "my-service-alarms-prod"
  sns_display_name = "My Service Alarms"

  alarm_config_path = "lambda/config"

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

### API Gateway Monitoring

```hcl
module "api_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-api"
  workspace_suffix = "-prod"

  sns_topic_name   = "my-api-alarms-prod"
  sns_display_name = "My API Gateway Alarms"

  alarm_config_path = "api-gateway/config"

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
module "waf_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-waf"
  workspace_suffix = "-prod"

  sns_topic_name   = "my-waf-alarms-prod"
  sns_display_name = "My WAF Alarms"

  alarm_config_path = "waf/config"

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
module "full_stack_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"

  sns_topic_name   = "my-service-alarms-prod"
  sns_display_name = "My Service Full Stack Alarms"

  alarm_config_path = "${path.module}/alarms/full-stack-config.json"

  monitored_resources = {
    api_lambda = module.api_lambda.lambda_function_name
    api        = module.api_gateway.api_name
    waf        = aws_wafv2_web_acl.main.name
  }

  alarm_thresholds = {
    api_lambda = {
      "duration-p99-critical"          = 3000
      "errors-critical"                = 5
      "throttles-critical"             = 0
      "concurrent-executions-critical" = 100
    }
    api = {
      "4xx-errors-warning"      = 100
      "5xx-errors-critical"     = 10
      "latency-p99-critical"    = 5000
      "request-spike-critical"  = 10000
    }
    waf = {
      "blocked-requests-warning"        = 1000
      "blocked-requests-critical"       = 5000
      "allowed-requests-spike-critical" = 50000
      "counted-requests-warning"        = 500
    }
  }

  # ... evaluation periods and periods
}
```

### Multiple Resources of Same Type

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"

  sns_topic_name   = "my-service-alarms-prod"
  sns_display_name = "My Service Alarms"

  alarm_config_path = "lambda/config"

  monitored_resources = {
    api_lambda    = module.api_lambda.lambda_function_name
    worker_lambda = module.worker_lambda.lambda_function_name
  }

  alarm_thresholds = {
    api_lambda = {
      "duration-p99-critical"          = 3000
      "errors-critical"                = 5
      "throttles-critical"             = 0
      "concurrent-executions-critical" = 100
    }
    worker_lambda = {
      "duration-p99-critical"          = 30000
      "errors-critical"                = 10
      "throttles-critical"             = 0
      "concurrent-executions-critical" = 50
    }
  }

  # ... evaluation periods and periods
}
```

### Separate Monitoring Modules per Resource Type

```hcl
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"
  alarm_config_path = "lambda/config"
  monitored_resources = {
    api_lambda    = module.api_lambda.lambda_function_name
    worker_lambda = module.worker_lambda.lambda_function_name
  }
  # ... configuration
}

module "api_monitoring" {
  source = "../../modules/cloudwatch-monitoring"
  alarm_config_path = "api-gateway/config"
  monitored_resources = {
    api = module.api_gateway.api_name
  }
  # ... configuration
}

module "waf_monitoring" {
  source = "../../modules/cloudwatch-monitoring"
  alarm_config_path = "waf/config"
  monitored_resources = {
    waf = aws_wafv2_web_acl.main.name
  }
  # ... configuration
}
```

### Custom Configuration

Create `alarms/custom-config.json`:

```json
{
  "api_lambda": [
    {
      "metric_name": "Duration",
      "statistic": "p99",
      "comparison_operator": "GreaterThanThreshold",
      "alarm_suffix": "duration-p99-critical",
      "description": "API Lambda duration p99 critical",
      "severity": "critical",
      "namespace": "AWS/Lambda",
      "dimension_name": "FunctionName"
    }
  ],
  "api": [
    {
      "metric_name": "5XXError",
      "statistic": "Sum",
      "comparison_operator": "GreaterThanThreshold",
      "alarm_suffix": "5xx-errors-critical",
      "description": "API Gateway 5XX errors critical",
      "severity": "critical",
      "namespace": "AWS/ApiGateway",
      "dimension_name": "ApiName"
    }
  ]
}
```

Use it:

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"
  alarm_config_path = "${path.module}/alarms/custom-config.json"
  monitored_resources = {
    api_lambda = module.api_lambda.lambda_function_name
    api        = module.api_gateway.api_name
  }
  # ... configuration
}
```

## Available Templates

| Resource Type | Template | Metrics Monitored | Use Case |
|--------------|----------|------------------|----------|
| **Lambda** | lambda/config | Duration (p99 warning/critical), Errors (warning/critical), Throttles, Concurrent Executions (warning/critical) | Standard Lambda monitoring |
| **API Gateway** | api-gateway/config | 4XX/5XX errors, Latency, Request counts | Standard API monitoring |
| **WAF** | waf/config | Blocked/Allowed/Counted requests | Standard WAF monitoring |

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
| alarm_config_path | Path to JSON alarm configuration or template name (e.g., 'lambda/config', 'api-gateway/config', 'waf/config') | string | no (default: 'lambda/config') |
| monitored_resources | Map of resource keys to their identifiers (Lambda names, API Gateway names, WAF WebACL names) | map(string) | yes |
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
