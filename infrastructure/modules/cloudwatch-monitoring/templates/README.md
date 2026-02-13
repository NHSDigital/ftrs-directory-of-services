# CloudWatch Monitoring Templates

This directory contains reusable alarm configuration templates for various AWS resources.

Templates automatically apply to all resources - no key matching required.

## Directory Structure

```text
templates/
├── lambda/          # Lambda function monitoring
├── api-gateway/     # API Gateway monitoring
└── waf/             # WAF WebACL monitoring
```

## Lambda Templates

### lambda/minimal.json

**Use for**: Basic production monitoring, low-traffic services

**Alarms**: Errors, Throttles

**Required thresholds**:

- `errors-critical`
- `throttles-critical`

### lambda/standard.json (Default)

**Use for**: Most production services

**Alarms**: Duration p99, Errors, Throttles, Concurrent Executions

**Required thresholds**:

- `duration-p99-critical`
- `errors-critical`
- `throttles-critical`
- `concurrent-executions-critical`

### lambda/comprehensive.json

**Use for**: High-criticality services

**Alarms**: All metrics with Warning + Critical levels

**Required thresholds**: All from standard + warning levels + invocations spike

## API Gateway Templates

### api-gateway/minimal.json

**Use for**: Basic API monitoring

**Alarms**:

- 5XX errors (critical)
- Latency p99 (critical)

**Required thresholds**:

- `5xx-errors-critical`
- `latency-p99-critical`

### api-gateway/standard.json

**Use for**: Production APIs

**Alarms**:

- 4XX errors (warning)
- 5XX errors (critical)
- Latency p99 (critical)
- Request spike (critical)

**Required thresholds**:

- `4xx-errors-warning`
- `5xx-errors-critical`
- `latency-p99-critical`
- `request-spike-critical`

## WAF Templates

### waf/minimal.json

**Use for**: Basic WAF monitoring

**Alarms**:

- Blocked requests (warning)
- Allowed requests spike (critical)

**Required thresholds**:

- `blocked-requests-warning`
- `allowed-requests-spike-critical`

### waf/standard.json

**Use for**: Production WAF monitoring

**Alarms**:

- Blocked requests (warning + critical)
- Allowed requests spike (critical)
- Counted requests (warning)

**Required thresholds**:

- `blocked-requests-warning`
- `blocked-requests-critical`
- `allowed-requests-spike-critical`
- `counted-requests-warning`

## Using Templates

### Lambda Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  alarm_config_path = "standard"  # Uses lambda/standard.json

  # Template applies to all lambda functions
  lambda_functions = {
    api_lambda    = module.api_lambda.lambda_function_name
    worker_lambda = module.worker_lambda.lambda_function_name
  }

  # Optional: only apply alarms to specific resources
  resource_type_filter = ["api_lambda"]  # Only api_lambda gets alarms

  # Define thresholds per function
  alarm_thresholds = {
    api_lambda = {
      "duration-p99-critical"          = 3000
      "errors-critical"                = 5
      "throttles-critical"             = 1
      "concurrent-executions-critical" = 100
    }
  }

  # ... evaluation periods and periods
}
```

### API Gateway Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

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

  # ... evaluation periods and periods
}
```

### WAF Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

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

  # ... evaluation periods and periods
}
```

### Multi-Resource Monitoring

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  # Use custom config with multiple resource types
  alarm_config_path = "${path.module}/alarms/multi-resource-config.json"

  monitored_resources = {
    api_lambda = module.api_lambda.lambda_function_name
    api        = module.api_gateway.api_name
    waf        = aws_wafv2_web_acl.main.name
  }

  # ... thresholds for all resources
}
```

## Custom Templates

Create your own template with the following structure:

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
- `statistic`: Statistical function
- `comparison_operator`: Comparison type
- `alarm_suffix`: Unique identifier for threshold mapping
- `description`: Human-readable description
- `severity`: `warning` or `critical`
- `namespace`: AWS service namespace
- `dimension_name`: Dimension name for the resource

## Supported Namespaces

| Namespace | Resource Type | Dimension Name |
| ----------- | --------------- | ---------------- |
| AWS/Lambda | Lambda functions | FunctionName |
| AWS/ApiGateway | API Gateway REST APIs | ApiName |
| AWS/ApiGateway | API Gateway HTTP APIs | ApiId |
| AWS/WAFV2 | WAF WebACLs | WebACL |

## Common Issues

### Alarms Not Created

**Symptom**: `terraform plan` shows no alarm resources being created

**Cause**: Missing thresholds in `alarm_thresholds` for your resources

**Solution**: Ensure each resource has thresholds defined for the alarms you want:

```hcl
alarm_thresholds = {
  my_lambda = {
    "errors-critical" = 5  # Must match alarm_suffix in template
  }
}
```

## Best Practices

1. **Define thresholds**: Only alarms with thresholds are created
2. **Start with templates**: Use built-in templates as a baseline
3. **Customize thresholds**: Adjust based on your service's behavior
4. **Monitor gradually**: Start with minimal, expand to standard/comprehensive
5. **Test alarms**: Trigger test alarms to verify notifications
6. **Document thresholds**: Keep track of why specific values were chosen
