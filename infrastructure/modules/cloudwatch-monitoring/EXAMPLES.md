# CloudWatch Monitoring Module - Usage Examples

## Example 1: Lambda Monitoring (Backward Compatible)

```hcl
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-service-alarms-prod"
  sns_display_name = "My Service Alarms"
  
  alarm_config_path = "lambda/standard"
  
  # Using lambda_functions (backward compatible)
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

## Example 2: API Gateway Monitoring

```hcl
module "api_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-api"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-api-alarms-prod"
  sns_display_name = "My API Gateway Alarms"
  
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

## Example 3: WAF Monitoring

```hcl
module "waf_monitoring" {
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

## Example 4: Multi-Resource Monitoring (Lambda + API Gateway + WAF)

```hcl
# Custom configuration file: alarms/full-stack-config.json
# {
#   "api_lambda": [ ... Lambda alarms ... ],
#   "api": [ ... API Gateway alarms ... ],
#   "waf": [ ... WAF alarms ... ]
# }

module "full_stack_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-service-alarms-prod"
  sns_display_name = "My Service Full Stack Alarms"
  
  # Custom config with all resource types
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
  
  alarm_evaluation_periods = {
    api_lambda = {
      "duration-p99-critical"          = 2
      "errors-critical"                = 2
      "throttles-critical"             = 1
      "concurrent-executions-critical" = 2
    }
    api = {
      "4xx-errors-warning"      = 3
      "5xx-errors-critical"     = 2
      "latency-p99-critical"    = 2
      "request-spike-critical"  = 1
    }
    waf = {
      "blocked-requests-warning"        = 2
      "blocked-requests-critical"       = 2
      "allowed-requests-spike-critical" = 1
      "counted-requests-warning"        = 2
    }
  }
  
  alarm_periods = {
    api_lambda = {
      "duration-p99-critical"          = 300
      "errors-critical"                = 300
      "throttles-critical"             = 60
      "concurrent-executions-critical" = 300
    }
    api = {
      "4xx-errors-warning"      = 300
      "5xx-errors-critical"     = 300
      "latency-p99-critical"    = 300
      "request-spike-critical"  = 3600
    }
    waf = {
      "blocked-requests-warning"        = 300
      "blocked-requests-critical"       = 300
      "allowed-requests-spike-critical" = 3600
      "counted-requests-warning"        = 300
    }
  }
}
```

## Example 5: Separate Monitoring Modules per Resource Type

```hcl
# Lambda monitoring
module "lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-service-lambda-alarms-prod"
  sns_display_name = "Lambda Alarms"
  
  alarm_config_path = "lambda/comprehensive"
  
  monitored_resources = {
    api_lambda    = module.api_lambda.lambda_function_name
    worker_lambda = module.worker_lambda.lambda_function_name
  }
  
  # ... thresholds
}

# API Gateway monitoring
module "api_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-service-api-alarms-prod"
  sns_display_name = "API Gateway Alarms"
  
  alarm_config_path = "api-gateway/standard"
  
  monitored_resources = {
    api = module.api_gateway.api_name
  }
  
  # ... thresholds
}

# WAF monitoring
module "waf_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-service-waf-alarms-prod"
  sns_display_name = "WAF Alarms"
  
  alarm_config_path = "waf/standard"
  
  monitored_resources = {
    waf = aws_wafv2_web_acl.main.name
  }
  
  # ... thresholds
}
```

## Example 6: Using New monitored_resources Variable

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix  = "my-service"
  workspace_suffix = "-prod"
  
  sns_topic_name   = "my-service-alarms-prod"
  sns_display_name = "My Service Alarms"
  
  alarm_config_path = "lambda/standard"
  
  # New approach: use monitored_resources
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

## Example 7: Custom Multi-Resource Configuration

Create `alarms/custom-multi-resource.json`:

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
  ],
  "waf": [
    {
      "metric_name": "BlockedRequests",
      "statistic": "Sum",
      "comparison_operator": "GreaterThanThreshold",
      "alarm_suffix": "blocked-requests-critical",
      "description": "WAF blocked requests critical",
      "severity": "critical",
      "namespace": "AWS/WAFV2",
      "dimension_name": "WebACL"
    }
  ]
}
```

Then use it:

```hcl
module "monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  alarm_config_path = "${path.module}/alarms/custom-multi-resource.json"
  
  monitored_resources = {
    api_lambda = module.api_lambda.lambda_function_name
    api        = module.api_gateway.api_name
    waf        = aws_wafv2_web_acl.main.name
  }
  
  # ... rest of configuration
}
```
