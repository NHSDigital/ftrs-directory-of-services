# CloudWatch Monitoring Templates

This directory contains reusable alarm configuration templates for various AWS resources.

Templates automatically apply to all resources - no key matching required.

## Directory Structure

```text
templates/
├── lambda/config.json          # Lambda function monitoring
├── api-gateway/config.json     # API Gateway monitoring
└── waf/config.json             # WAF WebACL monitoring
```

## Lambda Template

**File**: `lambda/config.json`

**Alarms**:

- Duration p99 (warning + critical)
- Errors (warning + critical)
- Throttles (critical)
- Concurrent Executions (warning + critical)

**Thresholds**:

- `duration-p99-warning` (optional)
- `duration-p99-critical` (optional)
- `errors-warning` (optional)
- `errors-critical` (optional)
- `throttles-critical` (optional)
- `concurrent-executions-warning` (optional)
- `concurrent-executions-critical` (optional)

## API Gateway Template

**File**: `api-gateway/config.json`

**Alarms**:

- 4XX errors (warning)
- 5XX errors (warning + critical)
- Latency p99 (warning + critical)
- Request spike (critical)

**Thresholds**:

- `4xx-errors-warning` (optional)
- `5xx-errors-warning` (optional)
- `5xx-errors-critical` (optional)
- `latency-p99-warning` (optional)
- `latency-p99-critical` (optional)
- `request-spike-critical` (optional)

## WAF Template

**File**: `waf/config.json`

**Alarms**:

- Blocked requests (warning + critical)
- Allowed requests spike (critical)
- Counted requests (warning)

**Thresholds**:

- `blocked-requests-warning` (optional)
- `blocked-requests-critical` (optional)
- `allowed-requests-spike-critical` (optional)
- `counted-requests-warning` (optional)

## Using Templates

### Lambda Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  alarm_config_path = "${path.module}/templates/lambda/config.json"

  monitored_resources = {
    api_lambda    = module.api_lambda.lambda_function_name
    worker_lambda = module.worker_lambda.lambda_function_name
  }

  alarm_thresholds = {
    api_lambda = {
      "duration-p99-warning"           = 2000
      "duration-p99-critical"          = 3000
      "errors-warning"                 = 3
      "errors-critical"                = 5
      "throttles-critical"             = 1
      "concurrent-executions-warning"  = 80
      "concurrent-executions-critical" = 100
    }
    worker_lambda = {
      "errors-critical"    = 10
      "throttles-critical" = 2
    }
  }

  alarm_evaluation_periods = {
    api_lambda = { "errors-critical" = 2 }
  }

  alarm_periods = {
    api_lambda = { "errors-critical" = 60 }
  }
}
```

### API Gateway Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  alarm_config_path = "${path.module}/templates/api-gateway/config.json"

  monitored_resources = {
    api = module.api_gateway.api_name
  }

  alarm_thresholds = {
    api = {
      "4xx-errors-warning"     = 100
      "5xx-errors-warning"     = 5
      "5xx-errors-critical"    = 10
      "latency-p99-warning"    = 3000
      "latency-p99-critical"   = 5000
      "request-spike-critical" = 10000
    }
  }

  alarm_evaluation_periods = {
    api = { "5xx-errors-critical" = 2 }
  }

  alarm_periods = {
    api = { "5xx-errors-critical" = 60 }
  }
}
```

### WAF Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  alarm_config_path = "${path.module}/templates/waf/config.json"

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
    waf = { "blocked-requests-critical" = 3 }
  }

  alarm_periods = {
    waf = { "blocked-requests-critical" = 300 }
  }
}
```

### Multi-Resource Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  alarm_config_path = "${path.module}/templates/custom-config.json"

  monitored_resources = {
    api_lambda = module.api_lambda.lambda_function_name
    api        = module.api_gateway.api_name
    waf        = aws_wafv2_web_acl.main.name
  }

  alarm_thresholds = {
    api_lambda = { "errors-critical" = 5 }
    api        = { "5xx-errors-critical" = 10 }
    waf        = { "blocked-requests-critical" = 5000 }
  }

  alarm_evaluation_periods = {
    api_lambda = { "errors-critical" = 2 }
    api        = { "5xx-errors-critical" = 2 }
    waf        = { "blocked-requests-critical" = 3 }
  }

  alarm_periods = {
    api_lambda = { "errors-critical" = 60 }
    api        = { "5xx-errors-critical" = 60 }
    waf        = { "blocked-requests-critical" = 300 }
  }
}
```

## Creating Additional Templates

You can create additional templates for specific use cases (e.g., minimal monitoring, comprehensive monitoring) by following the same structure as the default `config.json` files.

### Template Structure

```json
{
  "resource_type": [
    {
      "metric_name": "MetricName",
      "statistic": "Sum|Average|p99|etc",
      "comparison_operator": "GreaterThanThreshold",
      "alarm_suffix": "unique-identifier",
      "description": "Alarm description",
      "severity": "warning|critical",
      "namespace": "AWS/Lambda|AWS/ApiGateway|AWS/WAFV2",
      "dimension_name": "FunctionName|ApiName|WebACL"
    }
  ]
}
```

### Key Fields

- `resource_type`: Generic type (e.g., "lambda", "api", "waf") - template applies to all resources
- `metric_name`: CloudWatch metric name
- `statistic`: Statistical function (Sum, Average, p99, Maximum, etc.)
- `comparison_operator`: Comparison type (GreaterThanThreshold, LessThanThreshold, etc.)
- `alarm_suffix`: Unique identifier for threshold mapping
- `description`: Human-readable description
- `severity`: `warning` or `critical`
- `namespace`: AWS service namespace (AWS/Lambda, AWS/ApiGateway, AWS/WAFV2)
- `dimension_name`: Dimension name for the resource (FunctionName, ApiName, WebACL)

### Example: Minimal Lambda Template

Create `lambda/minimal-config.json` for basic monitoring:

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
    },
    {
      "metric_name": "Throttles",
      "statistic": "Sum",
      "comparison_operator": "GreaterThanThreshold",
      "alarm_suffix": "throttles-critical",
      "description": "Lambda throttles critical threshold",
      "severity": "critical"
    }
  ]
}
```

Then reference it:

```hcl
alarm_config_path = "${path.module}/templates/lambda/minimal-config.json"
```

## Supported AWS Services

| Service | Namespace | Resource Type | Dimension Name |
| ------- | --------- | ------------- | -------------- |
| Lambda | AWS/Lambda | lambda | FunctionName |
| API Gateway | AWS/ApiGateway | api | ApiName |
| WAF | AWS/WAFV2 | waf | WebACL |

## Best Practices

1. **Define thresholds**: Only alarms with defined thresholds are created
2. **Use templates as baseline**: Start with provided templates and customize as needed
3. **Adjust thresholds**: Tune based on actual service behavior and traffic patterns
4. **Test alarms**: Verify notifications work by triggering test alarms
5. **Document decisions**: Track why specific threshold values were chosen
6. **Review regularly**: Update thresholds as service usage patterns change
