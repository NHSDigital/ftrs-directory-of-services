#! /bin/bash

# This script triggers a Lambda function
# Introduced intially to run a Lambda to populate the SQS queue for data migration

# Fail on first error
set -e

export ENV="${ENV:-dev}"

# Check required environment variables
if [ -z "$FUNCTION_NAME" ] ; then
  echo "ERROR: FUNCTION_NAME is not set. Please export FUNCTION_NAME."
  exit 1
fi

# Invoke Lambda function
lambda_status=$(aws lambda invoke \
  --function-name "$FUNCTION_NAME"  \
  --invocation-type Event \
  response.json 2>&1)

# Check if the invocation was successful by parsing the status code
status_code=$(echo "$lambda_status" | jq -r '.StatusCode')

if [ "$status_code" -ne 202 ]; then
  echo "Lambda function invocation failed with status code $status_code"
  echo "Response: $lambda_status"
  exit 1
else
  echo "Lambda function invoked successfully"
fi

echo "Finished script to run $FUNCTION_NAME in $ENV"
