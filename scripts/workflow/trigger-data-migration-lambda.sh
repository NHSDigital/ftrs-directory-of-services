#! /bin/bash
# This script triggers a Lambda function
# Introduced intially to run lambda to populate the SQS queue for data migration
#
# fail on first error
set -e

export ENV="${ENV:-dev}"
# check exports have been done
EXPORTS_SET=0
# Check key variables have been exported - see above
if [ -z "$FUNCTION_NAME" ] ; then
  echo Set FUNCTION_NAME to name of lambda to trigger
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi
# start by invoking lambda to populate the queue
lambda_status=$(aws lambda invoke \
  --function-name "$FUNCTION_NAME"  \
  --invocation-type Event \
  response.json 2>&1)

status_code=$(echo "$lambda_status" | jq -r '.StatusCode')
if [ "$status_code" -ne 202 ]; then
  echo "Lambda function invocation failed with status code $status_code"
  echo "Response: $lambda_status"
  exit 1
else
  echo "Lambda function invoked successfully."
fi

echo "Finished script to run $FUNCTION_NAME in $ENV"

