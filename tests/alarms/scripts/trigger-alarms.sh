#!/usr/bin/env bash
set -euo pipefail

# Script to trigger CloudWatch alarms for testing
# Usage: ./trigger-alarms.sh <alarm-type> <lambda-type> [iterations]

ALARM_TYPE="${1:-}"
LAMBDA_TYPE="${2:-search}"
ITERATIONS="${3:-5}"
WORKSPACE="${WORKSPACE:-}"
ENVIRONMENT="${ENVIRONMENT:-}"

# Build AWS CLI profile argument if AWS_PROFILE is set
PROFILE_ARG=""
if [ -n "${AWS_PROFILE:-}" ]; then
  PROFILE_ARG="--profile $AWS_PROFILE"
fi

if [ -z "$ALARM_TYPE" ]; then
  echo "Usage: $0 <alarm-type> <lambda-type> [iterations]"
  echo ""
  echo "Alarm types:"
  echo "  errors              - Trigger error alarm by invoking with invalid payload"
  echo "  duration-p95        - Trigger duration p95 WARNING alarm"
  echo "  duration-p99        - Trigger duration p99 CRITICAL alarm"
  echo "  invocations-spike   - Trigger invocations spike CRITICAL alarm"
  echo "  throttles           - Trigger throttle CRITICAL alarm (requires reserved concurrency)"
  echo "  concurrent          - Trigger concurrent executions alarm"
  echo ""
  echo "Lambda types:"
  echo "  search          - DoS Search Lambda (default)"
  echo "  health-check    - Health Check Lambda"
  echo ""
  echo "Examples:"
  echo "  $0 errors search 2"
  echo "  $0 duration-p95 search 5"
  echo "  $0 concurrent search 85"
  exit 1
fi

# Determine Lambda function name
if [ "$LAMBDA_TYPE" = "search" ]; then
  LAMBDA_NAME="ftrs-dos-${ENVIRONMENT}-dos-search-ods-code-lambda"
elif [ "$LAMBDA_TYPE" = "health-check" ]; then
  LAMBDA_NAME="ftrs-dos-${ENVIRONMENT}-dos-search-health-check-lambda"
else
  echo "Error: Invalid lambda type. Use 'search' or 'health-check'"
  exit 1
fi

# Add workspace suffix if set
if [ -n "$WORKSPACE" ] && [ "$WORKSPACE" != "default" ]; then
  LAMBDA_NAME="${LAMBDA_NAME}-${WORKSPACE}"
fi

echo "Testing alarm: $ALARM_TYPE for Lambda: $LAMBDA_NAME"
echo "Iterations: $ITERATIONS"
echo ""

case "$ALARM_TYPE" in
  errors)
    echo "Triggering error alarm by invoking Lambda with invalid payload..."
    for i in $(seq 1 "$ITERATIONS"); do
      echo "Invocation $i/$ITERATIONS"
      aws lambda invoke \
        --function-name "$LAMBDA_NAME" \
        --payload '{"invalid":"event"}' \
        --cli-binary-format raw-in-base64-out \
        $PROFILE_ARG \
        /dev/null 2>&1 || true
      sleep 1
    done
    echo "✓ Triggered $ITERATIONS errors. Check CloudWatch alarm in ~2 minutes."
    echo "  - WARNING alarm: TBC once baseline is defined"
    echo "  - CRITICAL alarm: > 1 error over 2 periods (2 minutes)"
    ;;

  duration-p95)
    echo "Triggering duration p95 WARNING alarm (> TBC)..."
    echo "Note: This requires actual execution time > 600ms"
    for i in $(seq 1 "$ITERATIONS"); do
      echo "Invocation $i/$ITERATIONS"
      if [ "$LAMBDA_TYPE" = "search" ]; then
        aws lambda invoke \
          --function-name "$LAMBDA_NAME" \
          --payload '{"odsCode": "TEST123"}' \
          --cli-binary-format raw-in-base64-out \
          $PROFILE_ARG \
          /dev/null 2>&1 || true
      else
        aws lambda invoke \
          --function-name "$LAMBDA_NAME" \
          --cli-binary-format raw-in-base64-out \
          $PROFILE_ARG \
          /dev/null 2>&1 || true
      fi
      sleep 1
    done
    echo "✓ Triggered $ITERATIONS invocations. Check CloudWatch alarm in ~2 minutes."
    ;;

  duration-p99)
    echo "Triggering duration p99 CRITICAL alarm (> 800ms)..."
    echo "Note: This requires actual execution time > 800ms"
    for i in $(seq 1 "$ITERATIONS"); do
      echo "Invocation $i/$ITERATIONS"
      if [ "$LAMBDA_TYPE" = "search" ]; then
        aws lambda invoke \
          --function-name "$LAMBDA_NAME" \
          --payload '{"odsCode": "TEST123"}' \
          --cli-binary-format raw-in-base64-out \
          $PROFILE_ARG \
          /dev/null 2>&1 || true
      else
        aws lambda invoke \
          --function-name "$LAMBDA_NAME" \
          --cli-binary-format raw-in-base64-out \
          $PROFILE_ARG \
          /dev/null 2>&1 || true
      fi
      sleep 1
    done
    echo "✓ Triggered $ITERATIONS invocations. Check CloudWatch alarm in ~2 minutes."
    ;;

  invocations-spike)
    echo "Triggering invocations spike CRITICAL alarm..."
    echo "Baseline: 300/hour, Critical: > 600/hour (2x baseline)"
    echo "Invoking Lambda $ITERATIONS times immediately..."
    for i in $(seq 1 "$ITERATIONS"); do
      if [ "$LAMBDA_TYPE" = "search" ]; then
        aws lambda invoke \
          --function-name "$LAMBDA_NAME" \
          --payload '{"odsCode": "TEST123"}' \
          --cli-binary-format raw-in-base64-out \
          $PROFILE_ARG \
          /dev/null 2>&1 &
      else
        aws lambda invoke \
          --function-name "$LAMBDA_NAME" \
          --cli-binary-format raw-in-base64-out \
          $PROFILE_ARG \
          /dev/null 2>&1 &
      fi

      # Progress indicator every 50 invocations
      if [ $((i % 50)) -eq 0 ]; then
        echo "Progress: $i/$ITERATIONS invocations"
      fi
    done
    wait
    echo "✓ Triggered $ITERATIONS invocations. Check CloudWatch alarm in ~2 minutes."
    ;;

  throttles)
    echo "Triggering throttle CRITICAL alarm..."
    echo "Note: This requires reserved concurrency to be set on the Lambda function"
    echo "Invoking Lambda rapidly to cause throttling..."
    for i in $(seq 1 "$ITERATIONS"); do
      aws lambda invoke \
        --function-name "$LAMBDA_NAME" \
        --payload '{"odsCode": "TEST123"}' \
        --cli-binary-format raw-in-base64-out \
        $PROFILE_ARG \
        /dev/null 2>&1 &
    done
    wait
    echo "✓ Triggered $ITERATIONS concurrent invocations. Check for throttles in CloudWatch."
    echo "  - CRITICAL alarm: > 0 throttles for 1 minute"
    ;;

  concurrent)
    echo "Triggering concurrent executions alarm..."
    echo "  - WARNING: >= TBC concurrent executions"
    echo "  - CRITICAL: >= 100 concurrent executions"
    echo "Invoking Lambda concurrently ($ITERATIONS times)..."
    for i in $(seq 1 "$ITERATIONS"); do
      if [ "$LAMBDA_TYPE" = "search" ]; then
        aws lambda invoke \
          --function-name "$LAMBDA_NAME" \
          --payload '{"odsCode": "TEST123"}' \
          --cli-binary-format raw-in-base64-out \
          $PROFILE_ARG \
          /dev/null 2>&1 &
      else
        aws lambda invoke \
          --function-name "$LAMBDA_NAME" \
          --cli-binary-format raw-in-base64-out \
          $PROFILE_ARG \
          /dev/null 2>&1 &
      fi
    done
    wait
    echo "✓ Triggered $ITERATIONS concurrent invocations. Check CloudWatch alarm."
    ;;

  *)
    echo "Error: Unknown alarm type '$ALARM_TYPE'"
    echo "Valid types: errors, duration-p95, duration-p99, invocations-spike, throttles, concurrent"
    exit 1
    ;;
esac

echo ""
echo "View alarms at:"
echo "https://eu-west-2.console.aws.amazon.com/cloudwatch/home?region=eu-west-2#alarmsV2:"
