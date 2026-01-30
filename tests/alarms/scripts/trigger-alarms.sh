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
  echo "  errors          - Trigger error alarm by invoking with invalid payload"
  echo "  duration        - Trigger duration alarm (requires low threshold)"
  echo "  invocations     - Trigger low invocations alarm (wait for period)"
  echo "  throttles       - Trigger throttle alarm (requires reserved concurrency)"
  echo "  concurrent      - Trigger concurrent executions alarm"
  echo ""
  echo "Lambda types:"
  echo "  search          - DoS Search Lambda (default)"
  echo "  health-check    - Health Check Lambda"
  echo ""
  echo "Examples:"
  echo "  $0 errors search 10"
  echo "  $0 duration health-check 5"
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
        --payload '{"invalid": "payload"}' \
        --cli-binary-format raw-in-base64-out \
        $PROFILE_ARG \
        /dev/null 2>&1 || true
      sleep 1
    done
    echo "✓ Triggered $ITERATIONS errors. Check CloudWatch alarm in ~1 minute."
    ;;

  duration)
    echo "Triggering duration alarm..."
    echo "Note: This requires the duration threshold to be set low (e.g., 1ms)"
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
    echo "✓ Triggered $ITERATIONS invocations. Check CloudWatch alarm in ~1 minute."
    ;;

  invocations)
    echo "Triggering low invocations alarm..."
    echo "Note: This alarm triggers when invocations are BELOW threshold"
    echo "Simply wait for the evaluation period without invoking the Lambda"
    echo "Current time: $(date)"
    echo "Wait for ~2 minutes for the alarm to trigger..."
    ;;

  throttles)
    echo "Triggering throttle alarm..."
    echo "Note: This requires reserved concurrency to be set on the Lambda"
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
    ;;

  concurrent)
    echo "Triggering concurrent executions alarm..."
    echo "Invoking Lambda concurrently..."
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
    echo "Valid types: errors, duration, invocations, throttles, concurrent"
    exit 1
    ;;
esac

echo ""
echo "View alarms at:"
echo "https://eu-west-2.console.aws.amazon.com/cloudwatch/home?region=eu-west-2#alarmsV2:"
