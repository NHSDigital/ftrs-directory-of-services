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
- Use the troubleshooting commands below for specific alarm types

### Troubleshooting Errors Alarms

Check if errors are being recorded:

```bash
# Set Lambda name (adjust for workspace if needed)
LAMBDA_NAME="ftrs-dos-${ENVIRONMENT}-dos-search-ods-code-lambda"
[ -n "${WORKSPACE}" ] && [ "${WORKSPACE}" != "default" ] && LAMBDA_NAME="${LAMBDA_NAME}-${WORKSPACE}"

# View recent errors in CloudWatch Logs
aws logs tail /aws/lambda/${LAMBDA_NAME} \
  --follow \
  --filter-pattern "ERROR" \
  --profile ${AWS_PROFILE}

# Check error metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=${LAMBDA_NAME} \
  --start-time $(date -u -v-10M +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum \
  --profile ${AWS_PROFILE}
```

### Troubleshooting Duration Alarms

Verify actual execution time:

```bash
# Set Lambda name (adjust for workspace if needed)
LAMBDA_NAME="ftrs-dos-${ENVIRONMENT}-dos-search-ods-code-lambda"
[ -n "${WORKSPACE}" ] && [ "${WORKSPACE}" != "default" ] && LAMBDA_NAME="${LAMBDA_NAME}-${WORKSPACE}"

# Check execution time for a single invocation
aws lambda invoke \
  --function-name ${LAMBDA_NAME} \
  --payload '{"odsCode": "TEST123"}' \
  --cli-binary-format raw-in-base64-out \
  --log-type Tail \
  --profile ${AWS_PROFILE} \
  response.json | jq -r '.LogResult' | base64 -d | grep "Duration"

# Check p99 duration metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=${LAMBDA_NAME} \
  --start-time $(date -u -v-10M +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average,Maximum \
  --profile ${AWS_PROFILE}
```

If execution time is below the threshold (600ms for p95, 800ms for p99), the alarm won't trigger.

### Troubleshooting Concurrent Executions Alarms

Check current concurrency levels:

```bash
# Set Lambda name (adjust for workspace if needed)
LAMBDA_NAME="ftrs-dos-${ENVIRONMENT}-dos-search-ods-code-lambda"
[ -n "${WORKSPACE}" ] && [ "${WORKSPACE}" != "default" ] && LAMBDA_NAME="${LAMBDA_NAME}-${WORKSPACE}"

# Check concurrent executions metric
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name ConcurrentExecutions \
  --dimensions Name=FunctionName,Value=${LAMBDA_NAME} \
  --start-time $(date -u -v-10M +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Maximum \
  --profile ${AWS_PROFILE}

# Check account-level concurrency
aws lambda get-account-settings --profile ${AWS_PROFILE}
```

**Lowering the threshold for easier testing:**

The default threshold of 100 concurrent executions can be difficult to trigger. To make testing easier, temporarily lower it:

1. Edit `infrastructure/stacks/dos_search/variables.tf` line 178-182:

   ```terraform
   variable "search_lambda_concurrent_executions_critical" {
     description = "Search Lambda concurrency critical threshold (ConcurrentExecutions)"
     type        = number
     default     = 10  # Lowered from 100 for testing
   }
   ```

2. Apply the change: Running the workspace via pipeline.

3. Update the test to match: `./scripts/trigger-alarms.sh concurrent search 15`

4. After testing, revert the threshold back to 100

### Troubleshooting Throttles Alarms

Check if throttling is occurring:

```bash
# Set Lambda name (adjust for workspace if needed)
LAMBDA_NAME="ftrs-dos-${ENVIRONMENT}-dos-search-ods-code-lambda"
[ -n "${WORKSPACE}" ] && [ "${WORKSPACE}" != "default" ] && LAMBDA_NAME="${LAMBDA_NAME}-${WORKSPACE}"

# Check if reserved concurrency is set
aws lambda get-function-concurrency \
  --function-name ${LAMBDA_NAME} \
  --profile ${AWS_PROFILE}

# Check throttle metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Throttles \
  --dimensions Name=FunctionName,Value=${LAMBDA_NAME} \
  --start-time $(date -u -v-10M +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum \
  --profile ${AWS_PROFILE}
```

**Setting up reserved concurrency for testing:**

Throttles alarm requires reserved concurrency to be set. To enable testing:

```bash
# Set Lambda name (adjust for workspace if needed)
LAMBDA_NAME="ftrs-dos-${ENVIRONMENT}-dos-search-ods-code-lambda"
[ -n "${WORKSPACE}" ] && [ "${WORKSPACE}" != "default" ] && LAMBDA_NAME="${LAMBDA_NAME}-${WORKSPACE}"

# Set reserved concurrency to 5 (limits Lambda to 5 concurrent executions)
aws lambda put-function-concurrency \
  --function-name ${LAMBDA_NAME} \
  --reserved-concurrent-executions 5 \
  --profile ${AWS_PROFILE}

# Run the test (20 concurrent invocations will cause throttling)
make test-lambda-alarm-throttles-critical

# Remove reserved concurrency after testing
aws lambda delete-function-concurrency \
  --function-name ${LAMBDA_NAME} \
  --profile ${AWS_PROFILE}
```

### Troubleshooting Invocations Spike Alarms

Check invocation rate:

```bash
# Set Lambda name (adjust for workspace if needed)
LAMBDA_NAME="ftrs-dos-${ENVIRONMENT}-dos-search-ods-code-lambda"
[ -n "${WORKSPACE}" ] && [ "${WORKSPACE}" != "default" ] && LAMBDA_NAME="${LAMBDA_NAME}-${WORKSPACE}"

# Check invocations over the last hour
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=${LAMBDA_NAME} \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --profile ${AWS_PROFILE}
```

Alarm triggers when invocations exceed 600/hour (2x baseline of 300/hour).
