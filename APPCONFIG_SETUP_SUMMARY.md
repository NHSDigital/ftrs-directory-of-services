# AppConfig Alarm Thresholds Implementation Summary

## What Was Done

Your Lambda CloudWatch alarm configurations are now **AppConfig-driven**. Here's what was implemented:

### 1. **New Configuration File**

- **File**: `toggles/alarm-thresholds.json`
- Contains all alarm thresholds in JSON format
- Easy to edit and version control
- Includes thresholds for both search and health check lambdas

### 2. **Updated AppConfig Stack**

- **File**: `infrastructure/stacks/app_config/app_config.tf`
- Added new AppConfig application: `alarm-thresholds-appconfig`
- Reads from `toggles/alarm-thresholds.json`
- Available in all environments (dev, int, prod, etc.)

### 3. **Alarm Configuration Layer in dos_search Stack**

- **File**: `infrastructure/stacks/dos_search/appconfig_alarms.tf`
- Reads the JSON configuration file into Terraform locals
- Parses thresholds for use in alarm definitions
- All thresholds are centralized in one place

### 4. **Updated CloudWatch Alarms**

- **File**: `infrastructure/stacks/dos_search/lambda_cloudwatch_alarms.tf`
- All alarm definitions now reference AppConfig-sourced locals instead of variables
- Alarm descriptions include current threshold values
- Marked as "Managed via AppConfig" for clarity

### 5. **Documentation**

- **File**: `infrastructure/stacks/dos_search/APPCONFIG_ALARMS_GUIDE.md`
- Complete guide on how to update thresholds
- Examples for Lambda runtime configuration reading
- IAM permissions required for runtime access

## How to Use It

### Update Alarm Thresholds (Easy!)

1. **Edit the configuration file**:

   ```bash
   vim toggles/alarm-thresholds.json
   ```

2. **Update threshold values**:

   ```json
   {
     "searchLambda": {
       "duration": { "threshold_ms": 7000 },  // Changed from 5000
       "errors": { "threshold": 10 }           // Changed from 5
     }
   }
   ```

3. **Deploy changes** (from infrastructure/stacks/AppConfig):

   ```bash
   cd infrastructure/stacks/app_config
   terraform apply
   ```

4. **Deploy dos_search stack** (automatically picks up new values):

   ```bash
   cd infrastructure/stacks/dos_search
   terraform apply
   ```

**That's it!** No code changes, no rewriting alarm logic - just JSON values.

## Benefits

| Feature | Benefit |
|---------|---------|
| **Centralized Config** | All thresholds in one place |
| **No Redeployment** | Change thresholds without code changes |
| **Git History** | Complete audit trail of all changes |
| **Environment-Specific** | Different thresholds per environment |
| **Runtime Ready** | Lambdas can read live config without redeployment |
| **Easy Rollback** | Revert via Git if needed |

## Example Configuration

```json
{
  "searchLambda": {
    "duration": {
      "threshold_ms": 5000,
      "description": "Threshold in milliseconds for search Lambda average duration"
    },
    "concurrentExecutions": {
      "threshold": 100,
      "description": "Threshold for search Lambda concurrent executions"
    },
    "errors": {
      "threshold": 5,
      "description": "Threshold for search Lambda errors (sum over period)"
    },
    "invocations": {
      "threshold": 1,
      "description": "Minimum threshold for search Lambda invocations (alerts if below)"
    }
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
  },
  "slackNotifications": {
    "enabled": true,
    "webhookSecretName": "dos-search-slack-webhook-url"
  }
}
```

## Next Steps (Optional)

### For Lambda Runtime Configuration

If you want Lambdas to read thresholds at runtime (without redeployment):

1. Add AppConfig permissions to Lambda IAM role (see guide)
2. Import AppConfig boto3 client in Lambda code
3. Call `get_configuration()` to fetch live thresholds
4. Use thresholds for custom logic (circuit breakers, retries, etc.)

### Monitor Drift

Keep an eye on Terraform state to ensure AppConfig and alarms stay in sync:

```bash
terraform plan  # Should show no changes after applying
```

## Files Modified/Created

- ✅ `toggles/alarm-thresholds.json` - NEW
- ✅ `toggles/feature-flags.json` - NEW (placeholder for future)
- ✅ `infrastructure/stacks/app_config/app_config.tf` - UPDATED
- ✅ `infrastructure/stacks/dos_search/appconfig_alarms.tf` - NEW
- ✅ `infrastructure/stacks/dos_search/lambda_cloudwatch_alarms.tf` - UPDATED (all references changed)
- ✅ `infrastructure/stacks/dos_search/APPCONFIG_ALARMS_GUIDE.md` - NEW

## Questions?

See `APPCONFIG_ALARMS_GUIDE.md` for detailed documentation on:
- Architecture overview
- Configuration structure
- Runtime Lambda usage
- Troubleshooting
