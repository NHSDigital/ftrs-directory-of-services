#!/usr/bin/env bash
set -euo pipefail

SECRET_NAME="${1:-/ftrs-dos/dev/dos-search-proxygen-jwt-credentials}"
REGION="${2:-${AWS_REGION:-${AWS_DEFAULT_REGION:-eu-west-2}}}"

echo "--- Debug secrets script ---"
echo "Region: $REGION"

echo "--- AWS caller identity ---"
aws sts get-caller-identity --output json || true

echo "Account: $(aws sts get-caller-identity --query Account --output text || true)"

echo "--- aws configure list ---"
aws configure list || true

echo "--- List Secrets matching /ftrs-dos or dos-search ---"
aws secretsmanager list-secrets --region "$REGION" \
  --query "SecretList[?contains(Name,'/ftrs-dos') || contains(Name,'dos-search')].{Name:Name,ARN:ARN}" --output table || true

# Resolve secret ARN if present
SECRET_ARN=$(aws secretsmanager list-secrets --region "$REGION" --query "SecretList[?Name=='${SECRET_NAME}'].ARN | [0]" --output text 2>/dev/null || true)

if [ -n "$SECRET_ARN" ] && [ "$SECRET_ARN" != "None" ]; then
  echo "Resolved secret ARN: $SECRET_ARN"
  aws secretsmanager get-secret-value --secret-id "$SECRET_ARN" --region "$REGION" --query SecretString --output text || echo "SECRET READ FAILED (by ARN)"
else
  echo "No ARN resolved for $SECRET_NAME; trying by name"
  aws secretsmanager get-secret-value --secret-id "$SECRET_NAME" --region "$REGION" --query SecretString --output text || echo "SECRET READ FAILED (by name)"
fi

echo "--- End debug secrets script ---"

