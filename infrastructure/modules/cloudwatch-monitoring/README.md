# CloudWatch Monitoring Module

Reusable Terraform module for AWS resource monitoring with CloudWatch alarms and SNS notifications.

## Quick Start

Use built-in templates for Lambda, API Gateway, or WAF monitoring. Simply specify your resources and thresholds.

Note: API and WAF templates are currently placeholders. They'll be adjusted accordingly in future tickets

### Lambda Monitoring

```hcl
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix      = "my-service"
  sns_topic_name       = "my-service-lambda-alarms"
  sns_display_name     = "My Service Lambda Alarms"
  alarm_config_path    = "lambda/config"

  monitored_resources = {
    api_lambda    = module.api_lambda.lambda_function_name
    worker_lambda = module.worker_lambda.lambda_function_name
  }

  alarm_thresholds = {
    api_lambda = {
      "duration-p95-warning"           = 2000
      "duration-p99-critical"          = 3000
      "errors-warning"                 = 3
      "errors-critical"                = 5
      "throttles-critical"             = 0
      "concurrent-executions-warning"  = 80
      "concurrent-executions-critical" = 100
      "invocations-spike-critical"     = 10000
    }
    worker_lambda = {
      "duration-p95-warning"           = 20000
      "duration-p99-critical"          = 30000
      "errors-warning"                 = 5
      "errors-critical"                = 10
      "throttles-critical"             = 0
      "concurrent-executions-warning"  = 40
      "concurrent-executions-critical" = 50
      "invocations-spike-critical"     = 5000
    }
  }

  alarm_evaluation_periods = {
    api_lambda = {
      "duration-p95-warning"           = 2
      "duration-p99-critical"          = 2
      "errors-warning"                 = 2
      "errors-critical"                = 2
      "throttles-critical"             = 1
      "concurrent-executions-warning"  = 2
      "concurrent-executions-critical" = 2
      "invocations-spike-critical"     = 1
    }
    worker_lambda = {
      "duration-p95-warning"           = 2
      "duration-p99-critical"          = 2
      "errors-warning"                 = 2
      "errors-critical"                = 2
      "throttles-critical"             = 1
      "concurrent-executions-warning"  = 2
      "concurrent-executions-critical" = 2
      "invocations-spike-critical"     = 1
    }
  }

  alarm_periods = {
    api_lambda = {
      "duration-p95-warning"           = 300
      "duration-p99-critical"          = 300
      "errors-warning"                 = 300
      "errors-critical"                = 300
      "throttles-critical"             = 60
      "concurrent-executions-warning"  = 300
      "concurrent-executions-critical" = 300
      "invocations-spike-critical"     = 3600
    }
    worker_lambda = {
      "duration-p95-warning"           = 300
      "duration-p99-critical"          = 300
      "errors-warning"                 = 300
      "errors-critical"                = 300
      "throttles-critical"             = 60
      "concurrent-executions-warning"  = 300
      "concurrent-executions-critical" = 300
      "invocations-spike-critical"     = 3600
    }
  }

  tags = {
    Environment = "prod"
    Service     = "my-service"
  }
}
```

### API Gateway Monitoring

```hcl
module "api_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix      = "my-api"
  sns_topic_name       = "my-api-alarms"
  sns_display_name     = "My API Gateway Alarms"
  alarm_config_path    = "api-gateway/config"

  monitored_resources = {
    api = module.api_gateway.api_name
  }

  alarm_thresholds = {
    api = {
      "4xx-errors-warning"     = 100
      "5xx-errors-critical"    = 10
      "latency-p99-critical"   = 5000
      "request-spike-critical" = 10000
    }
  }

  alarm_evaluation_periods = {
    api = {
      "4xx-errors-warning"     = 3
      "5xx-errors-critical"    = 2
      "latency-p99-critical"   = 2
      "request-spike-critical" = 1
    }
  }

  alarm_periods = {
    api = {
      "4xx-errors-warning"     = 300
      "5xx-errors-critical"    = 300
      "latency-p99-critical"   = 300
      "request-spike-critical" = 3600
    }
  }
}
```

### WAF Monitoring

```hcl
module "waf_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix      = "my-waf"
  sns_topic_name       = "my-waf-alarms"
  sns_display_name     = "My WAF Alarms"
  alarm_config_path    = "waf/config"

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

## Available Templates

| Template | Metrics Monitored |
|----------|-------------------|
| `lambda/config` | Duration (p95, p99), Errors, Throttles, Concurrent Executions, Invocation Spikes |
| `api-gateway/config` | 4XX/5XX Errors, Latency (p99), Request Spikes |
| `waf/config` | Blocked/Allowed/Counted Requests |

## Configuration

### Required Inputs

| Name | Description | Example |
|------|-------------|----------|
| `resource_prefix` | Prefix for alarm names | `"my-service"` |
| `sns_topic_name` | SNS topic name | `"my-service-alarms"` |
| `sns_display_name` | SNS topic display name | `"My Service Alarms"` |
| `alarm_config_path` | Template to use | `"lambda/config"` |
| `monitored_resources` | Resources to monitor | `{ api_lambda = "my-function" }` |
| `alarm_thresholds` | Threshold values per resource | See examples above |
| `alarm_evaluation_periods` | Evaluation periods per resource | See examples above |
| `alarm_periods` | Period in seconds per resource | See examples above |

### Optional Inputs

| Name | Description | Default |
|------|-------------|----------|
| `kms_key_id` | KMS key for SNS encryption | `null` |
| `enable_warning_alarms` | Enable warning severity alarms | `false` |
| `tags` | Tags for SNS topic | `{}` |

## Outputs

| Name | Description |
|------|-------------|
| `sns_topic_arn` | ARN of the SNS topic |
| `sns_topic_name` | Name of the SNS topic |
| `alarm_arns` | Map of alarm names to ARNs |

## Integration with Slack

The SNS topic created by this module can be subscribed to by the slack-notifier service for alarm notifications to Slack channels.
