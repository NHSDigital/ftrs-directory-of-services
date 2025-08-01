#! /bin/bash

# Script to manage DynamoDB backups:
# - Creates a new backup for each target table with a commit-specific name.
# - Retains only the latest N backups (default: 3).
# - Stores new backup ARNs in AWS SSM Parameter Store.

# Fail on first error
set -e

export MAX_BACKUPS="${MAX_BACKUPS:-3}"
export ENV="${ENV:-dev}"

# Check required environment variables
if [ -z "$COMMIT_HASH" ] ; then
  echo "ERROR: COMMIT_HASH is not set. Please export COMMIT_HASH to the short form commit hash."
  exit 1
fi

if [ -z "$DYNAMO_PREFIX_NAME" ] ; then
  echo "ERROR: DYNAMO_PREFIX_NAME is not set. Please export DYNAMO_PREFIX_NAMEDYNAMO_TABLE_NAME to the name of the DynamoDB table to manage backups for."
  exit 1
fi

TABLE_NAME=("healthcare-service" "location" "organisation")
ARN_JSON=()

echo "Starting DynamoDB backup management for environment: $ENV"

# -------------------------
# Backup Logic
# -------------------------

for table in "${TABLE_NAME[@]}"; do

  FULL_TABLE_NAME="$DYNAMO_PREFIX_NAME-$table"
  BACKUP_NAME="${FULL_TABLE_NAME}-${COMMIT_HASH}"

  echo "Creating backup for $FULL_TABLE_NAME with commit hash $BACKUP_NAME"
  create_output=$(aws dynamodb create-backup --table-name "$FULL_TABLE_NAME" --backup-name "$BACKUP_NAME"  2>&1 )
  new_arn=$(echo "$create_output" | jq -r '.BackupDetails.BackupArn')
  echo "Backup created: $new_arn"

  # Track new ARN
  ARN_JSON+=("$(jq -n --arg table "$table" --arg new_arn "$new_arn" '{($table): $new_arn}')" )

  echo "Checking backup retention for $FULL_TABLE_NAME (max: $MAX_BACKUPS)..."
  list_output=$(aws dynamodb list-backups --table-name "$FULL_TABLE_NAME" --backup-type USER \
  | jq '.[] | sort_by(.BackupCreationDate)' 2>&1)
  echo "$list_output"
  backup_count=0
  earliest_backup_arn=""

  list_output=$(aws dynamodb list-backups --table-name "$FULL_TABLE_NAME" --backup-type USER)
  backup_arns=($(echo "$list_output" | jq -r '.BackupSummaries | sort_by(.BackupCreationDateTime) | .[].BackupArn'))

  if [[ ${#backup_arns[@]} -gt $MAX_BACKUPS ]]; then
    to_delete="${backup_arns[0]}"
    echo "Exceeding $MAX_BACKUPS backups for $FULL_TABLE_NAME. Deleting oldest: $to_delete"
    delete_output=$(aws dynamodb delete-backup --backup-arn "$to_delete" 2>&1)
    deleted_name=$(echo "$delete_output" | jq -r '.BackupDescription.BackupDetails.BackupName')
    echo "Deleted backup: $deleted_name"
  else
    echo "Backup count within limit: ${#backup_arns[@]} (limit: $MAX_BACKUPS)"
  fi

  echo "Finished backup management for $FULL_TABLE_NAME"
done

# -------------------------
# Store to Parameter Store
# -------------------------

SSM_NAME="/ftrs-dos/${ENV}/dynamodb-tables-backup-arns"
SSM_VALUE=$(printf '%s\n' "${ARN_JSON[@]}" | jq -s add)

echo "Storing latest backup ARNs to SSM Parameter: $SSM_NAME"
aws ssm put-parameter --name "$SSM_NAME" --value "$SSM_VALUE" --type "String" --overwrite

echo "Backup ARNs stored in SSM: $SSM_NAME"
echo "Backup management completed for environment: $ENV"
