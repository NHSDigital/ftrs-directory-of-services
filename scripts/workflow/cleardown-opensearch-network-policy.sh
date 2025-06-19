#! /bin/bash

# Exit immediately on error]
set -e
EXPORTS_SET=0

# Check for required environment variables
if [[ -z "$WORKSPACE" ]]; then
  echo "Error: WORKSPACE is not set"
  EXPORTS_SET=1
fi

if [[ -z "$STACK" ]]; then
  echo "Error: STACK is not set"
  EXPORTS_SET=1
fi

if [[ $EXPORTS_SET -eq 1 ]]; then
  echo "One or more required environment variables are missing. Exiting."
  exit 1
fi

echo "Current terraform workspace is --> $WORKSPACE"

if [[ "${STACK}" == "opensearch" ]]; then
  # Optional: Clean up orphaned OpenSearch Ingestion Network Policies
  echo "Checking for OpenSearch Ingestion Network Policies to delete."

  # Define pattern for network policy name — adjust as needed
  NETWORK_POLICY_NAME="pipeline-${STACK}-nap-${WORKSPACE}"

  # Fetch matching policy name(s)
  policy_arn=$(aws opensearchserverless list-security-policies \
    --type network \
    --query "securityPolicySummaries[?name=='${NETWORK_POLICY_NAME}'].name" \
    --output text)

  if [ -n "$policy_arn" ]; then
    echo "Found matching OpenSearch network policy: $policy_arn"
    aws opensearchserverless delete-security-policy \
      --type network \
      --name "$policy_arn"
    echo "Successfully deleted network policy: $policy_arn"
  else
    echo "No matching OpenSearch network policy found for deletion"
  fi
fi
