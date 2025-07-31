#! /bin/bash

# fail on first error
set -e
EXPORTS_SET=0

export MAX_BACKUPS="${MAX_BACKUPS:-3}"
export ENV="${ENV:-dev}"
# check necessary environment variables are set

if [ -z "$COMMIT_HASH" ] ; then
  echo Set COMMIT_HASH to short form commit hash
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

table_name_prefix="ftrs-dos-${ENV}-database"

TABLE_NAME=("healthcare-service" "location" "organisation")

arn_array=()

for table in "${TABLE_NAME[@]}"; do

FULL_TABLE_NAME="$table_name_prefix-$table"
# First create new backup and then check to see if have one to delete
echo "Managing backups for $FULL_TABLE_NAME starting..."
echo "Creating new backup for $FULL_TABLE_NAME with commit hash $COMMIT_HASH"
create_output=$(aws dynamodb create-backup --table-name "$FULL_TABLE_NAME" --backup-name "$FULL_TABLE_NAME-$COMMIT_HASH"  2>&1 )
echo "$create_output" | jq -r '.BackupDetails | "Backup ARN: \(.BackupArn)\nBackup Name: \(.BackupName)"' 2>&1
new_arn=$(echo "$create_output" | jq -r '.BackupDetails.BackupArn')
# create json object with table name and new arn
echo -e "New backup ARN: $new_arn"
json_arn=$(jq -c -n --arg table "$table" --arg new_arn "$new_arn" '{($table): $new_arn}')
# add json object to array
arn_array+=("$json_arn")

list_output=$(aws dynamodb list-backups --table-name "$FULL_TABLE_NAME" --backup-type USER \
| jq '.[] | sort_by(.BackupCreationDate)' 2>&1)
echo "$list_output"
backup_count=0
earliest_backup_arn=""
while read -r backup; do
  backup_arn=$(echo "$backup" | jq -r '.BackupArn')
  backup_creation_date=$(echo "$backup" | jq -r '.BackupCreationDateTime')
  echo -e "Backup ARN: $backup_arn \nCreation Date: $backup_creation_date"
  # handle case where no backups exist
  if [ -n "$backup_arn" ]; then
    backup_count=$((backup_count + 1))
  fi
  if [ $backup_count -eq 1 ]; then
    earliest_backup_arn=$backup_arn
  fi

done <<EOT
$(jq -c '.[]' <<< "$list_output")
EOT

if [ $backup_count -gt "$MAX_BACKUPS" ]; then
  echo -e "Surplus backups ($backup_count) for $FULL_TABLE_NAME \nPreparing to delete earliest one - $earliest_backup_arn"
  delete_output=$(aws dynamodb delete-backup --backup-arn "$earliest_backup_arn" 2>&1)
  echo "Deleted..."
  echo "$delete_output" | jq -r '.BackupDescription.BackupDetails | "Backup ARN: \(.BackupArn)\nBackup Name: \(.BackupName)"' 2>&1
else
  echo "$backup_count backups at or below threshold $MAX_BACKUPS. No backups deleted."
fi

echo "Finished backup management for $FULL_TABLE_NAME"

done

# store newest backup arns in ssm parameter
ssm_parameter_value=$(printf '%s\n' "${arn_array[@]}" | jq -s --compact-output)
echo "SSM Parameter Value: $ssm_parameter_value"

parameter_output=$(aws ssm put-parameter --name "/ftrs/dos/${ENV}/dynamodb-backup-arns" \
  --value "$ssm_parameter_value" --type "String" --overwrite 2>&1)
echo "$parameter_output"
echo "Stored backup ARNs in SSM parameter /ftrs-dos-${ENV}-database-tables-backup-arns"

echo "Finished backup management script for environment: $ENV"

