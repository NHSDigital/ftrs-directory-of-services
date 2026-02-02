# CloudWatch Alarm Testing

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
   export WORKSPACE=your-workspace  # optional, if using workspaces i.e ftrs-765
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
**make** test-lambda-alarm-errors-warning
```

This targets: `ftrs-dos-dev-dos-search-ods-code-lambda`

**For feature branch workspace:**

```bash
# Set your AWS profile
export AWS_PROFILE=ftrs-dev

# Set environment and workspace
export ENVIRONMENT=dev
export WORKSPACE=ftrs-765

# Trigger an error alarm for the search Lambda
make test-lambda-alarm-errors-warning
```

This targets: `ftrs-dos-dev-dos-search-ods-code-lambda-ftrs-765`

## Available Make Targets

### Search Lambda Alarms

- `make test-lambda-alarm-errors-warning` - Trigger error WARNING alarm (2 errors)
- `make test-lambda-alarm-errors-critical` - Trigger error CRITICAL alarm (2 errors)
- `make test-lambda-alarm-duration-p95` - Trigger duration p95 WARNING alarm (> 600ms)
- `make test-lambda-alarm-duration-p99` - Trigger duration p99 CRITICAL alarm (> 800ms)
- `make test-lambda-alarm-concurrent-warning` - Trigger concurrent WARNING alarm (>= 80)
- `make test-lambda-alarm-concurrent-critical` - Trigger concurrent CRITICAL alarm (>= 100)
- `make test-lambda-alarm-throttles` - Trigger throttle CRITICAL alarm
- `make test-lambda-alarm-invocations-spike` - Trigger invocations spike CRITICAL alarm (> 600/hour)

### Health Check Lambda Alarms

- `make test-lambda-alarm-errors-health` - Trigger error CRITICAL alarm for health check

### Run All Tests

- `make test-lambda-alarms-all` - Run multiple alarm tests sequentially

## Alarm Configuration

Alarm thresholds are configured in [`infrastructure/stacks/dos_search/variables.tf`](../../infrastructure/stacks/dos_search/variables.tf).

**Note**: WARNING severity alarms are currently **disabled** (actions_enabled = false) and serve as placeholders. Only CRITICAL alarms are active. WARNING thresholds will be defined after establishing baselines during private beta.

### Search Lambda Alarms (Active)

| Metric | Severity | Threshold | Evaluation | Period | Status |
|--------|----------|-----------|------------|--------|--------|
| Duration (p99) | CRITICAL | > 800ms | 2/3 periods | 60s | ✅ Active |
| Concurrent Executions | CRITICAL | >= 100 | 2/3 periods | 60s | ✅ Active |
| Throttles | CRITICAL | > 0 | 1/1 period | 60s | ✅ Active |
| Invocations | CRITICAL | > 600/hour | 2/3 periods | 3600s | ✅ Active |
| Errors | CRITICAL | > 1 | 2/3 periods | 60s | ✅ Active |

### Search Lambda Alarms (Placeholders - Disabled)

| Metric | Severity | Threshold | Status |
|--------|----------|-----------|--------|
| Duration (p95) | WARNING | TBD (placeholder: 600ms) | ⏸️ Disabled |
| Concurrent Executions | WARNING | TBD (placeholder: 80) | ⏸️ Disabled |
| Errors | WARNING | TBD (placeholder: 5) | ⏸️ Disabled |

### Health Check Lambda Alarms

| Metric | Severity | Threshold | Evaluation | Period | Status |
|--------|----------|-----------|------------|--------|--------|
| Errors | CRITICAL | > 0 | 1/1 period | 60s | ✅ Active |

## Alarm Details

### Errors (WARNING - DISABLED)

**Status**: Placeholder alarm - actions disabled until baseline established.

**Placeholder threshold**: 5
**Time to trigger**: N/A (disabled)
**Variable**: `search_lambda_errors_warning_threshold`
**Enable**: Set `enable_warning_alarms = true` in variables.tf

### Errors (CRITICAL - ACTIVE)

Triggers by invoking Lambda with invalid payloads that cause errors.

**Requirements**: None
**Time to trigger**: ~3 minutes (2 out of 3 periods must breach)
**Variable**: `search_lambda_errors_critical_threshold`

### Duration p95 (WARNING - DISABLED)

**Status**: Placeholder alarm - actions disabled until baseline established.

**Placeholder threshold**: 600ms
**Time to trigger**: N/A (disabled)
**Variable**: `search_lambda_duration_p95_warning_ms`
**Enable**: Set `enable_warning_alarms = true` in variables.tf

### Duration p99 (CRITICAL - ACTIVE)

Triggers when Lambda p99 execution time exceeds 800ms.

**Requirements**: Actual execution time must exceed 800ms
**Time to trigger**: ~3 minutes (2 out of 3 periods must breach)
**Variable**: `search_lambda_duration_p99_critical_ms`

### Concurrent Executions (WARNING - DISABLED)

**Status**: Placeholder alarm - actions disabled until baseline established.

**Placeholder threshold**: 80
**Time to trigger**: N/A (disabled)
**Variable**: `search_lambda_concurrent_executions_warning`
**Enable**: Set `enable_warning_alarms = true` in variables.tf

### Concurrent Executions (CRITICAL - ACTIVE)

Triggers when too many Lambda instances run simultaneously.

**Requirements**: Sufficient concurrent invocations (>= 100)
**Time to trigger**: ~3 minutes (2 out of 3 periods must breach)
**Variable**: `search_lambda_concurrent_executions_critical` (100)

### Throttles (CRITICAL - ACTIVE)

Triggers when Lambda is throttled due to concurrency limits.

**Requirements**: Reserved concurrency must be set on the Lambda function
**Time to trigger**: Immediate when throttling occurs (1 minute evaluation)
**Variable**: `search_lambda_throttles_critical_threshold` (0)

### Invocations Spike (CRITICAL - ACTIVE)

Triggers when Lambda invocations exceed 2x baseline (600/hour).

**Requirements**: > 600 invocations in 1 hour
**Time to trigger**: ~3 minutes (2 out of 3 periods must breach)
**Variables**: `search_lambda_invocations_baseline_per_hour` (300), `invocations_critical_spike_multiplier` (2)

### Health Check Errors (CRITICAL - ACTIVE)

Triggers when health check Lambda has any errors.

**Requirements**: None
**Time to trigger**: ~1 minute after error
**Variable**: `health_check_errors_critical_threshold` (0)

## Direct Script Usage

You can also use the script directly for more control:

```bash
# Basic usage
./scripts/trigger-alarms.sh <alarm-type> <lambda-type> [iterations]

# Examples
./scripts/trigger-alarms.sh errors search 2
./scripts/trigger-alarms.sh duration-p95 search 5
./scripts/trigger-alarms.sh concurrent search 85
./scripts/trigger-alarms.sh invocations-spike search 650
```

## Viewing Results

After triggering alarms, view them in the AWS Console:

- [CloudWatch Alarms Console](https://eu-west-2.console.aws.amazon.com/cloudwatch/home?region=eu-west-2#alarmsV2:)

Or check Slack notifications in the configured alerts channel (#ftrs-dos-search-alarms)

## Troubleshooting

**"SSO session expired" or "Unable to locate credentials" error**:

- Login using AWS SSO: `aws sso login --profile <your-profile-name>`
- Verify your session is active: `aws sts get-caller-identity --profile <your-profile-name>`

**"Function not found" error**:

- Verify `ENVIRONMENT` and `WORKSPACE` variables are set correctly
- Check Lambda function name matches: `ftrs-dos-{ENVIRONMENT}-dos-search-ods-code-lambda[-{WORKSPACE}]`

**"Access denied" error**:

- Verify your AWS profile has permissions to invoke Lambda functions
- Check you're using the correct AWS profile: `echo $AWS_PROFILE`

**Alarms not triggering**:

- Wait 1-2 minutes for CloudWatch to evaluate metrics
- Check alarm thresholds in Terraform configuration
- Verify alarm evaluation periods and thresholds are appropriate for testing
- For duration alarms, ensure Lambda execution time actually exceeds thresholds

**Lambda Logging**:

- Check CloudWatch Logs for the Lambda function to see invocation details and errors using:

```shell
aws lambda get-function --function-name ftrs-dos-dev-dos-search-slack-notification-ftrs-765 --profile dos-search-dev
```

`ftrs-765` is your workspace and will need to adjusted according to yours.
`--profile <your-profile name>` is your AWS CLI name that you used when you configured AWS CLI using `aws configure sso`.
