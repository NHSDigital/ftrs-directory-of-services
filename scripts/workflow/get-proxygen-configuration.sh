#!/bin/bash

# Script to retrieve Proxygen configuration (token URL and Proxygen URL) from AWS Secrets Manager
# Required environment variables: ENV, API_NAME

set -e

# Get the secret string
PROXYGEN_CONFIGURATION=$(aws secretsmanager get-secret-value \
    --secret-id /ftrs-dos/"$ENV"/"$API_NAME"-proxygen-jwt-credentials \
    --query SecretString \
    --output text)

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PROXYGEN_CONFIGURATION="$PROXYGEN_CONFIGURATION" python3 "$SCRIPT_DIR/convert-to-json.py"

if [[ -z "$PROXYGEN_CONFIGURATION" ]]; then
    echo "Error: Failed to retrieve Proxygen configuration" >&2
    exit 1
fi

echo "Successfully retrieved Proxygen configuration" >&2
echo "$PROXYGEN_CONFIGURATION"
