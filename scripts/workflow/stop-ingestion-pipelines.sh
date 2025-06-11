#! /bin/bash
# This script stops all active ingestion pipelines in all workspaces in the specified AWS region.
# It is intended primarily for use in non-production environments to ensure that no ingestion pipelines
# are running unless actually required.
# fail on first error
set -e

echo "Stopping any active ingestion pipelines for all tables in all workspaces in region ${AWS_REGION}"

aws osis list-pipelines \
  --region "${AWS_REGION}" | jq -r '.Pipelines[] | select( .Status | contains("ACTIVE") ) | .PipelineName' | while read -r name; \
  do \
    echo "Stopping pipeline ${name}";
    aws osis stop-pipeline \
    --pipeline-name "${name}" \
    --region "${AWS_REGION}" | \
    jq -r '.Pipeline | .Status'
  done


