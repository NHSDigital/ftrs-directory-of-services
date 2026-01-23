# Alarm Thresholds Management via AppConfig

## Overview

Alarm thresholds for the DoS Search Lambda functions are managed through **AWS AppConfig as the source of truth**. This allows operational teams to update alarm configurations via the AWS Console without code changes or redeployment.

## Architecture

```hcl
Initial Setup (One-time):
   toggles/alarm-thresholds.json
           ↓
      terraform apply (app_config stack)
           ↓
      AWS AppConfig Created
           ↓
      terraform apply (dos_search stack)
           ↓
      CloudWatch Alarms Created

Ongoing Updates (No Redeployment):
   AWS AppConfig Console (GUI Update)
           ↓
      terraform apply (dos_search stack)
           ↓
      CloudWatch Alarms Updated
           ↓
      Changes take effect immediately
```

## Files

- **[toggles/alarm-thresholds.json](../../toggles/alarm-thresholds.json)** - Initial configuration template
- **[infrastructure/stacks/app_config/app_config.tf](../../infrastructure/stacks/app_config/app_config.tf)** - Creates AppConfig application
- **[infrastructure/stacks/dos_search/appconfig_alarms.tf](../dos_search/appconfig_alarms.tf)** - **Reads LIVE AppConfig values** via data source
- **[infrastructure/stacks/dos_search/lambda_cloudwatch_alarms.tf](../dos_search/lambda_cloudwatch_alarms.tf)** - Defines CloudWatch alarms using AppConfig values
- **[infrastructure/stacks/dos_search/data.tf](../dos_search/data.tf)** - Provides remote state access to AppConfig outputs

## Configuration Structure

```json
{
  "searchLambda": {
    "duration": { "threshold_ms": 5000 },
    "concurrentExecutions": { "threshold": 100 },
    "errors": { "threshold": 5 },
    "invocations": { "threshold": 1 }
  },
  "healthCheckLambda": {
    "duration": { "threshold_ms": 3000 },
    "concurrentExecutions": { "threshold": 50 },
    "errors": { "threshold": 3 },
    "invocations": { "threshold": 1 }
  },
  "alarmConfiguration": {
    "evaluationPeriods": 2,
    "periodSeconds": 300
  }
}
```

## How to Update Alarm Thresholds

### Option 1: Via AWS AppConfig GUI (Recommended for Operations)

This is the primary way ops teams update thresholds **without code changes or redeployment**.

1. Go to **AWS AppConfig** in AWS Console
2. Find application: `{environment}-dos-search-alarm-thresholds`
3. Navigate to **Hosted Configuration Versions**
4. Edit the JSON configuration with new threshold values
5. Create new deployment (configuration is now live)
6. Run `terraform apply` in dos_search stack **to sync Terraform state**

**Important:** Running `terraform apply` syncs the live AppConfig values into Terraform state. Terraform will read the current AppConfig content, not from the local file.

### Option 2: Via Infrastructure Code (Better Audit Trail)

For changes with full Git history:

1. Edit `toggles/alarm-thresholds.json`
   ```json
   "searchLambda": {
     "duration": { "threshold_ms": 7000 }  // Changed from 5000 to 7000
   }
   ```

2. Deploy changes to AppConfig stack:
   ```bash
   cd infrastructure/stacks/app_config
   terraform apply
   ```

3. Deploy dos_search stack (reads updated AppConfig):
   ```bash
   cd infrastructure/stacks/dos_search
   terraform apply
   ```

## Workflow Comparison

| Aspect | GUI Updates | Code Updates |
|--------|-------------|--------------|
| **Time to Effect** | Immediate (after terraform apply) | Requires Git commit + terraform apply |
| **Audit Trail** | AWS AppConfig history | Git history + Terraform state |
| **Best For** | Operational tuning | Permanent configuration changes |
| **Rollback** | AppConfig version history | Git revert |

**Recommendation:** Use GUI for temporary tuning, Git for permanent changes.

## Reading AppConfig at Runtime (Lambda)

Lambdas can read live thresholds from AppConfig at runtime without redeployment:

```python
import boto3
import json
from functools import lru_cache

appconfig = boto3.client('appconfig')

@lru_cache(maxsize=1)
def get_alarm_thresholds():
    """Read alarm thresholds from AppConfig with caching"""
    response = appconfig.get_configuration(
        Application='prod-dos-search-alarm-thresholds',
        Environment='prod',
        Configuration='alarm-thresholds',
        ClientId='search-lambda-v1'
    )

    config = json.loads(response['Content'].read())
    return config

def lambda_handler(event, context):
    thresholds = get_alarm_thresholds()

    duration_threshold = thresholds['searchLambda']['duration']['threshold_ms']
    error_threshold = thresholds['searchLambda']['errors']['threshold']

    # Use thresholds for custom logic, retries, circuit breakers, etc.
    if execution_time > duration_threshold:
        print(f"Warning: Execution exceeded {duration_threshold}ms threshold")

    return {'statusCode': 200}
```

### Lambda IAM Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "appconfig:GetConfiguration"
      ],
      "Resource": "arn:aws:appconfig:*:ACCOUNT_ID:application/*/environment/*/configuration-profile/*"
    }
  ]
}
```

## Terraform Integration

The dos_search stack reads the configuration file directly:

```hcl
locals {
  alarm_config_file = file("${path.root}/../../toggles/alarm-thresholds.json")
  alarm_config      = jsondecode(local.alarm_config_file)

  search_lambda_duration_threshold_ms = local.alarm_config.searchLambda.duration.threshold_ms
  # ... other threshold values ...
}

resource "aws_cloudwatch_metric_alarm" "search_lambda_duration" {
  threshold = local.search_lambda_duration_threshold_ms
  # ...
}
```

## Benefits

✅ **Centralized Configuration** - Single source of truth
✅ **No Code Changes** - Update thresholds without modifying Terraform
✅ **Audit Trail** - Git history shows all configuration changes
✅ **Environment-Specific** - Different thresholds per environment via AppConfig environments
✅ **Runtime Flexibility** - Lambdas can read live config without redeployment
✅ **Easy Rollback** - Git history allows instant rollback

## Future Enhancements

- Add dynamic threshold adjustment based on traffic patterns
- Create Lambda function to automatically update thresholds based on CloudWatch metrics
- Add feature flags to enable/disable specific alarms via AppConfig
- Implement alarm template management for different workload types

