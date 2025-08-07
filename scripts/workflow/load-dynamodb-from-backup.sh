#!/bin/bash

# Script to load DynamoDB tables with data from a backup:
# - Restores tables from a backup stored in AWS SSM Parameter Store.
# - Checks if the tables are empty before restoring.

# Fail on first error
set -e

export ENV="${ENV:-dev}"

# Check required environment variables
if [ -z "$WORKSPACE" ] ; then
  echo "ERROR: WORKSPACE is not set. Please export WORKSPACE to the name of the workspace."
  exit 1
fi

if [ -z "$DYNAMO_PREFIX_NAME" ] ; then
  echo "ERROR: DYNAMO_PREFIX_NAME is not set. Please export DYNAMO_PREFIX_NAME to the name of the DynamoDB table to restore from backup."
  exit 1
fi

TABLE_NAME=("healthcare-service" "organisation" "location")
SSM_NAME="/ftrs-dos/${ENV}/dynamodb-tables-backup-arns"

echo "Restoring DynamoDB tables for $WORKSPACE..."
echo "Fetching backup ARNs from SSM parameter: $SSM_NAME"

# Fetch and parse the SSM parameter value
backup_json=$(aws ssm get-parameter --name "$SSM_NAME" --with-decryption --output json \
  | jq -r '.Parameter.Value')

# Loop through each table and attempt restore if it's empty
for table in "${TABLE_NAME[@]}"; do
  TARGET_TABLE="$DYNAMO_PREFIX_NAME-$table-$WORKSPACE"
  echo "Checking table: $TARGET_TABLE"

  item_count=$(aws dynamodb scan --table-name "$TARGET_TABLE" --select "COUNT" \
    --output json | jq -r '.Count')

  if [[ "$item_count" -gt 0 ]]; then
    echo "Table $TARGET_TABLE already has $item_count items. Skipping restore."
    continue
  fi

  BACKUP_ARN=$(echo "$backup_json" | jq -r --arg table "$table" '.[$table]')

  if [[ -z "$BACKUP_ARN" || "$BACKUP_ARN" == "null" ]]; then
    echo "No backup ARN found for $table. Skipping restore."
    continue
  fi

  echo "Restoring $TARGET_TABLE from backup: $BACKUP_ARN"
  aws dynamodb restore-table-from-backup \
    --target-table-name "$TARGET_TABLE" \
    --backup-arn "$BACKUP_ARN"

  echo "Restore initiated for $TARGET_TABLE"
done

echo "DynamoDB restore completed successfully."
