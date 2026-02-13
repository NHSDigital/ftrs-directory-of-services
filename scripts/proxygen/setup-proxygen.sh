#!/bin/bash

# Usage: API_NAME=<api name> ENVIRONMENT=<environment> ./setup-proxygen.sh
#
# Prerequisites:
#   - asdf installed
#   - yq installed
#   - AWS CLI configured and logged in
#   - Environment variables set:
#     - API_NAME (e.g., dos-search)
#     - ENVIRONMENT (e.g., dev)
#
# Example:
#   API_NAME=dos-search ENVIRONMENT=dev ./setup-proxygen.sh

set -e

# Check if proxygen is already installed and working
if ! command -v proxygen >/dev/null 2>&1; then
    echo "proxygen-cli is not installed."
    read -p "Do you want to install proxygen-cli? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled. Please install proxygen-cli manually."
        exit 1
    fi

    echo "Installing proxygen-cli..."

    # Check if asdf is installed
    if ! command -v asdf >/dev/null 2>&1; then
        echo "Error: asdf is not installed. Please install asdf first."
        exit 1
    fi

    # Install pipx using asdf
    asdf plugin add pipx || true  # Don't fail if plugin already exists
    asdf install pipx latest
    asdf set -u pipx latest

    # Install proxygen-cli using pipx
    pipx install proxygen-cli

    # Verify installation
    if command -v proxygen >/dev/null 2>&1; then
        echo "proxygen-cli installed successfully"
    else
        echo "Error: proxygen-cli installation failed"
        echo "Have you added the asdf shims directory to your path?"
        echo "For ZSH, add the following to ~/.zshrc:"
        echo "  export PATH=\"\${ASDF_DATA_DIR:-\$HOME/.asdf}/shims:\$PATH\""
        exit 1
    fi
fi


# Check if yq is installed
if ! command -v yq >/dev/null 2>&1; then
    echo "Error: yq is not installed. Please install yq first."
    exit 1
fi

# Check if AWS is logged in
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "Error: AWS credentials not configured or expired. Please log in to AWS first."
    exit 1
fi

# Check if required environment variables are set
if [ -z "$API_NAME" ]; then
    echo "Error: API_NAME environment variable is not set."
    exit 1
fi

if [ -z "$ENVIRONMENT" ]; then
    echo "Error: ENVIRONMENT environment variable is not set."
    exit 1
fi

# Configuration
SECRET_ID="/ftrs-dos/${ENVIRONMENT}/${API_NAME}-proxygen-jwt-credentials"
PROXYGEN_DIR="$HOME/.proxygen"
CREDENTIALS_FILE="$PROXYGEN_DIR/credentials.yaml"
SETTINGS_FILE="$PROXYGEN_DIR/settings.yaml"

# Create proxygen directory if it doesn't exist
mkdir -p "$PROXYGEN_DIR"

echo "Fetching JWT credentials from AWS Secrets Manager..."

# Get the secret and parse values
SECRET_JSON=$(aws secretsmanager get-secret-value --secret-id "$SECRET_ID" --query SecretString --output text)

CLIENT_ID=$(echo "$SECRET_JSON" | yq -r '.client_id')
KID=$(echo "$SECRET_JSON" | yq -r '.kid')
PRIVATE_KEY=$(echo "$SECRET_JSON" | yq -r '.private_key')
TOKEN_URL=$(echo "$SECRET_JSON" | yq -r '.token_url')

# Extract PROXYGEN_API_NAME from CLIENT_ID
PROXYGEN_API_NAME=${CLIENT_ID%-client}

# Extract base URL from token URL
BASE_URL=${TOKEN_URL//\/protocol\/openid-connect\/token/}

PRIVATE_KEY_FILE="$PROXYGEN_DIR/$KID.pem"

# Create timestamped backups if files exist
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
[[ -f "$CREDENTIALS_FILE" ]] && cp "$CREDENTIALS_FILE" "${CREDENTIALS_FILE}.backup_${TIMESTAMP}"
[[ -f "$SETTINGS_FILE" ]] && cp "$SETTINGS_FILE" "${SETTINGS_FILE}.backup_${TIMESTAMP}"
[[ -f "$PRIVATE_KEY_FILE" ]] && cp "$PRIVATE_KEY_FILE" "${PRIVATE_KEY_FILE}.backup_${TIMESTAMP}"

echo "Writing private key to $PRIVATE_KEY_FILE..."
echo "$PRIVATE_KEY" > "$PRIVATE_KEY_FILE"

echo "Writing credentials to $CREDENTIALS_FILE..."
touch "$CREDENTIALS_FILE"
BASE_URL=$BASE_URL CLIENT_ID=$CLIENT_ID KID=$KID PRIVATE_KEY_FILE=$PRIVATE_KEY_FILE \
  yq eval '
    .base_url = env(BASE_URL) |
    .client_id = env(CLIENT_ID) |
    .key_id = env(KID) |
    .private_key_path = env(PRIVATE_KEY_FILE) |
    .username = "" |
    .password = ""
  ' -i "$CREDENTIALS_FILE"

echo "Writing settings to $SETTINGS_FILE..."
touch "$SETTINGS_FILE"
PROXYGEN_API_NAME=$PROXYGEN_API_NAME \
  yq eval '
    .api = env(PROXYGEN_API_NAME) |
    .endpoint_url = "https://proxygen.ptl.api.platform.nhs.uk" |
    .spec_output_format = "yaml"
  ' -i "$SETTINGS_FILE"

echo "Proxygen configuration complete!"
echo "Files updated:"
echo "  - $CREDENTIALS_FILE"
echo "  - $SETTINGS_FILE"
echo "  - $PRIVATE_KEY_FILE"
