# Cloudwatch Alarm Testing

This directory contains tools for testing CloudWatch alarms by triggering them manually.

## Prerequisites

1. **Make**: This guide assumes you have GNU Make installed and configured. If not, see the [main repository README](../../README.md#prerequisites) for setup instructions including asdf installation
2. **AWS Credentials**: Ensure you have AWS credentials configured
3. **AWS Profile**: Set your AWS profile environment variable:
   ```bash
   export AWS_PROFILE=your-profile-name
   ```
4. **Environment Variables**: Set required environment variables:
   ```bash
   export ENVIRONMENT=dev  # or test, prod, etc.
   export WORKSPACE=your-workspace  # optional, if using workspaces
   ```

## Quick Start

From the `tests/alarms` directory:

**For main environment (no workspace):**
```bash
# Set your AWS profile
export AWS_PROFILE=ftrs-dev

# Set environment
export ENVIRONMENT=dev

# Trigger an error alarm for the search Lambda
make test-lambda-alarm-errors
```
This targets: `ftrs-dos-dev-dos-search-ods-code-lambda`

**For feature branch workspace:**
```bash
# Set your AWS profile (replace ftrs-dev with your profile name)
export AWS_PROFILE=ftrs-dev

# Set environment and workspace (replace ftrs-765 with your workspace name)
export ENVIRONMENT=dev
export WORKSPACE=ftrs-765

# Trigger an error alarm for the search Lambda
make test-lambda-alarm-errors
```
This targets: `ftrs-dos-dev-dos-search-ods-code-lambda-ftrs-765` (where `ftrs-765` is your workspace)

## Available Make Targets

### Search Lambda Alarms

- `make test-lambda-alarm-errors` - Trigger error alarm (10 invalid invocations)
- `make test-lambda-alarm-duration` - Trigger duration alarm (5 invocations)
- `make test-lambda-alarm-concurrent` - Trigger concurrent executions alarm (10 concurrent invocations)
- `make test-lambda-alarm-throttles` - Trigger throttle alarm (20 rapid invocations)
- `make test-lambda-alarm-invocations` - Info on low invocations alarm

### Health Check Lambda Alarms

- `make test-lambda-alarm-errors-health` - Trigger error alarm for health check
- `make test-lambda-alarm-duration-health` - Trigger duration alarm for health check
- `make test-lambda-alarm-concurrent-health` - Trigger concurrent executions for health check
- `make test-lambda-alarm-throttles-health` - Trigger throttle alarm for health check

### Run All Tests

- `make test-lambda-alarms-all` - Run multiple alarm tests sequentially

## Alarm Types

**Note**: Alarm thresholds are configured in [`infrastructure/stacks/dos_search/variables.tf`](../../infrastructure/stacks/dos_search/variables.tf) (Line 136 onwards). Adjust these values to control when alarms trigger.

### Errors
Triggers by invoking Lambda with invalid payloads that cause errors.

**Requirements**: None
**Time to trigger**: ~1 minute after invocations
**Threshold variable**: `search_lambda_errors_threshold` or `health_check_lambda_errors_threshold`

### Duration
Triggers when Lambda execution time exceeds threshold.

**Requirements**: Duration threshold must be set low (e.g., 1ms) in Terraform
**Time to trigger**: ~1 minute after invocations
**Threshold variable**: `search_lambda_duration_threshold_ms` or `health_check_lambda_duration_threshold_ms`

### Concurrent Executions
Triggers when too many Lambda instances run simultaneously.

**Requirements**: Concurrent execution threshold set appropriately
**Time to trigger**: Immediate during concurrent invocations
**Threshold variable**: `search_lambda_concurrent_executions_threshold` or `health_check_lambda_concurrent_executions_threshold`

### Throttles
Triggers when Lambda is throttled due to concurrency limits.

**Requirements**: Reserved concurrency must be set on the Lambda function
**Time to trigger**: Immediate when throttling occurs
**Threshold variable**: `search_lambda_throttles_threshold` or `health_check_lambda_throttles_threshold`

### Invocations (Low)
Triggers when Lambda invocations fall below expected threshold.

**Requirements**: None
**Time to trigger**: ~2 minutes of no invocations
**Threshold variable**: `search_lambda_invocations_threshold` or `health_check_lambda_invocations_threshold`

## Direct Script Usage

You can also use the script directly for more control:

```bash
# Basic usage
./scripts/trigger-alarms.sh <alarm-type> <lambda-type> [iterations]

# Examples
./scripts/trigger-alarms.sh errors search 10
./scripts/trigger-alarms.sh duration health-check 5
./scripts/trigger-alarms.sh concurrent search 20
```

## Viewing Results

After triggering alarms, view them in the AWS Console:
- [CloudWatch Alarms Console](https://eu-west-2.console.aws.amazon.com/cloudwatch/home?region=eu-west-2#alarmsV2:)

Or check Slack notifications in the configured alerts channel (`#ftrs-dos-search-alerts`)

## Troubleshooting

**"SSO session expired" or "Unable to locate credentials" error**:
- Login using AWS SSO: `aws sso login --profile <your-profile-name>` (e.g., `aws sso login --profile dos-search-dev`)
- Verify your session is active: `aws sts get-caller-identity --profile <your-profile-name>`

**"Function not found" error**:
- Verify `ENVIRONMENT` and `WORKSPACE` variables are set correctly
- Check Lambda function name matches: `ftrs-dos-{ENVIRONMENT}-dos-search-ods-code-lambda[-{WORKSPACE}]` or `ftrs-dos-{ENVIRONMENT}-dos-search-health-check-lambda[-{WORKSPACE}]`
- Example: `ftrs-dos-dev-dos-search-ods-code-lambda-ftrs-765`

**"Access denied" error**:
- Verify your AWS profile has permissions to invoke Lambda functions
- Check you're using the correct AWS profile: `echo $AWS_PROFILE`

**Alarms not triggering**:
- Wait 1-2 minutes for CloudWatch to evaluate metrics
- Check alarm thresholds in Terraform configuration
- Verify alarm evaluation periods and thresholds are appropriate for testing
