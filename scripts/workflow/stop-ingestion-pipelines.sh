#! /bin/bash
# This script stops all active ingestion pipelines in all workspaces in the specified AWS region.
# It is intended primarily for use in non-production environments to ensure that no ingestion pipelines
# are running unless actually required.


echo "Stopping any active ingestion pipelines for all tables in all workspaces in region ${AWS_REGION}"

OUTCOME=0
aws osis list-pipelines \
  --region "${AWS_REGION}" | jq -r '.Pipelines[] | select( .Status | contains("ACTIVE") ) | .PipelineName' | while read -r PIPELINE_NAME; \
  do \
    echo "Stopping pipeline ${PIPELINE_NAME}"
    RESPONSE=$(aws osis stop-pipeline \
    --pipeline-name "${PIPELINE_NAME}" \
    --region "${AWS_REGION}" | \
    jq -r '.Pipeline | .Status')
    echo "${RESPONSE}"
    if [ "${RESPONSE}" != "STOPPING" ]; then
      echo "Pipeline ${PIPELINE_NAME} did not stop successfully"
      OUTCOME=1
    fi
  done
  exit ${OUTCOME}


