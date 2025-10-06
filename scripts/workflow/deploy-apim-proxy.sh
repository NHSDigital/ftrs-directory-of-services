#!/bin/bash

# AWS Secrets Manager retrieval and Proxygen deployment script for GitHub Actions
# This script fetches secrets, retrieves private key from S3, sets up Proxygen credentials, and deploys

set -euo pipefail

# Define the secret paths (excluding private key which will come from S3)
SECRETS=(
    "/ftrs-dos/dev/proxygen-key-id"
    "/ftrs-dos/dev/proxygen-client-id"
    "/ftrs-dos/dev/proxygen-public-key"
    "/temp/dev/api-ca-cert"
    "/temp/dev/api-ca-pk"
)

# Define corresponding output variable names
OUTPUT_VARS=(
    "PROXYGEN_KEY_ID"
    "PROXYGEN_CLIENT_ID"
    "PROXYGEN_PUBLIC_KEY"
    "API_CA_CERT"
    "API_CA_PK"
)

# S3 configuration for private key
S3_BUCKET=""
S3_PRIVATE_KEY_PATH="ftrs-dos/dev/proxygen-private-key"
PROXYGEN_PRIVATE_KEY_FILE="/tmp/proxygen-private-key.pem"

# Proxygen configuration
PROXYGEN_INSTANCE="internal-dev"
PROXYGEN_SERVICE_NAME="ftrs-search-<workspace>" # not sure how to handle workspace here
OASPEC_FILE="docs/specification/dos-search.yaml"
PROXYGEN_CONFIG_FILE="/tmp/proxygen-config.json"

echo "=== Starting Proxygen Deployment Process ==="

# Check if required CLI tools are available
check_dependencies() {
    local deps=("aws" "proxygen" "yq")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            echo "Error: $dep is not installed or not in PATH"
            exit 1
        fi
    done
    echo "✓ All dependencies available (including Proxygen CLI and yq)"
}

# Function to retrieve and output secret
retrieve_secret() {
    local secret_path="$1"
    local output_var="$2"

    echo "Retrieving secret: $secret_path"

    # Retrieve the secret value
    local secret_value
    if secret_value=$(aws secretsmanager get-secret-value --secret-id "$secret_path" --query 'SecretString' --output text 2>/dev/null); then
        # Export as environment variable
        export "$output_var"="$secret_value"

        # Mask the secret in GitHub Actions logs
        echo "::add-mask::$secret_value"
        echo "$output_var=***MASKED***" >> $GITHUB_ENV

        echo "✓ Successfully retrieved $output_var"
    else
        echo "Error: Failed to retrieve secret $secret_path"
        exit 1
    fi
}

# Function to retrieve private key from S3
retrieve_private_key_from_s3() {
    echo "Retrieving private key from S3: s3://$S3_BUCKET/$S3_PRIVATE_KEY_PATH"

    if aws s3 cp "s3://$S3_BUCKET/$S3_PRIVATE_KEY_PATH" "$PROXYGEN_PRIVATE_KEY_FILE" 2>/dev/null; then
        # Set proper permissions for private key
        chmod 600 "$PROXYGEN_PRIVATE_KEY_FILE"

        # Export path as environment variable
        export PROXYGEN_PRIVATE_KEY="$PROXYGEN_PRIVATE_KEY_FILE"
        echo "PROXYGEN_PRIVATE_KEY=$PROXYGEN_PRIVATE_KEY_FILE" >> $GITHUB_ENV

        echo "✓ Successfully retrieved private key from S3"
    else
        echo "Error: Failed to retrieve private key from S3"
        exit 1
    fi
}

# Function to set up Proxygen CLI credentials
setup_proxygen_auth() {
    echo "Setting up Proxygen CLI credentials..."

    # Set Proxygen credentials using the credentials set command
    echo "Running: proxygen credentials set private_key_path $PROXYGEN_PRIVATE_KEY key_id $PROXYGEN_KEY_ID client_id $PROXYGEN_CLIENT_ID"

    if proxygen credentials set \
        private_key_path "$PROXYGEN_PRIVATE_KEY" \
        key_id "$PROXYGEN_KEY_ID" \
        client_id "$PROXYGEN_CLIENT_ID"; then
        echo "✓ Proxygen CLI credentials configured successfully"

        # Verify credentials are set
        echo "Verifying Proxygen credentials..."
        if proxygen credentials show 2>/dev/null; then
            echo "✓ Credentials verification successful"
        else
            echo "⚠ Could not verify credentials, but set command succeeded"
        fi
    else
        echo "Error: Failed to set Proxygen CLI credentials"
        echo "Command failed: proxygen credentials set private_key_path $PROXYGEN_PRIVATE_KEY key_id $PROXYGEN_KEY_ID client_id $PROXYGEN_CLIENT_ID"
        exit 1
    fi
}

# Function to preprocess OAS specification file
preprocess_oaspec() {
    echo "Preprocessing OpenAPI specification file..."

    local workspace="${WORKSPACE:-dev}"
    local backup_file="${OASPEC_FILE}.backup"

    # Create backup of original file
    if [[ -f "$OASPEC_FILE" ]]; then
        echo "Creating backup: $backup_file"
        cp "$OASPEC_FILE" "$backup_file"
    else
        echo "Error: OpenAPI spec file '$OASPEC_FILE' not found"
        exit 1
    fi

    # Preprocess the OAS file - prefix title with workspace tag
    echo "Prefixing title with workspace tag: [$workspace]"

    if yq eval ".info.title = \"[\" + \"$workspace\" + \"] \" + .info.title" "$backup_file" > "$OASPEC_FILE"; then
        echo "✓ Successfully preprocessed OAS file"

        # Show the updated title for verification
        local new_title
        if new_title=$(yq eval '.info.title' "$OASPEC_FILE" 2>/dev/null); then
            echo "Updated title: $new_title"
        fi
    else
        echo "Error: Failed to preprocess OAS file"
        echo "Restoring original file..."
        mv "$backup_file" "$OASPEC_FILE"
        exit 1
    fi

    # Optionally show other info that was modified
    echo "OAS file preprocessing completed successfully"
}

# Function to validate OpenAPI spec file
validate_oaspec() {
    echo "Validating OpenAPI specification file..."

    if [[ ! -f "$OASPEC_FILE" ]]; then
        echo "Error: OpenAPI spec file '$OASPEC_FILE' not found"
        echo "Please ensure the oaspec.yaml file exists in the current directory"
        exit 1
    fi

    # Basic validation of YAML format
    if ! yq eval '.' "$OASPEC_FILE" > /dev/null 2>&1; then
        echo "Error: OpenAPI spec file has YAML syntax issues"
        exit 1
    fi

    # Validate that required OpenAPI fields exist
    local title version
    title=$(yq eval '.info.title // ""' "$OASPEC_FILE" 2>/dev/null)
    version=$(yq eval '.info.version // ""' "$OASPEC_FILE" 2>/dev/null)

    if [[ -z "$title" ]]; then
        echo "Warning: OpenAPI spec missing info.title"
    fi

    if [[ -z "$version" ]]; then
        echo "Warning: OpenAPI spec missing info.version"
    fi

    echo "✓ OpenAPI specification file validated: $OASPEC_FILE"
    [[ -n "$title" ]] && echo "  Title: $title"
    [[ -n "$version" ]] && echo "  Version: $version"
}

# Function to deploy to Proxygen using CLI
deploy_to_proxygen() {
    echo "Starting deployment to Proxygen using CLI..."

    # Expand workspace variable if it exists
    local service_name="$PROXYGEN_SERVICE_NAME"
    if [[ "$service_name" == *"<workspace>"* ]]; then
        # Replace <workspace> with actual workspace value if available
        local workspace="${WORKSPACE:-dev}"
        service_name="${service_name/<workspace>/$workspace}"
        echo "Expanded service name: $service_name"
    fi

    echo "Deploying with parameters:"
    echo "  Instance: $PROXYGEN_INSTANCE"
    echo "  Service: $service_name"
    echo "  Spec file: $OASPEC_FILE"

    # Execute the Proxygen deployment command
    echo "Running: proxygen instance deploy $PROXYGEN_INSTANCE $service_name $OASPEC_FILE"

    if proxygen instance deploy "$PROXYGEN_INSTANCE" "$service_name" "$OASPEC_FILE"; then
        echo "✅ Proxygen deployment completed successfully!"

        # Get deployment status
        echo "Checking deployment status..."
        if proxygen instance status "$PROXYGEN_INSTANCE" "$service_name"; then
            echo "✓ Deployment status retrieved successfully"
        else
            echo "⚠ Could not retrieve deployment status, but deployment command succeeded"
        fi

    else
        echo "❌ Proxygen deployment failed!"
        echo "Command: proxygen instance deploy $PROXYGEN_INSTANCE $service_name $OASPEC_FILE"
        exit 1
    fi
}

# Function to list Proxygen deployments (optional verification)
list_proxygen_deployments() {
    echo "Listing current Proxygen deployments for verification..."

    if proxygen instance list "$PROXYGEN_INSTANCE"; then
        echo "✓ Successfully listed deployments"
    else
        echo "⚠ Could not list deployments, but this is non-critical"
    fi
}

# Cleanup function
cleanup() {
    echo "Cleaning up temporary files..."
    rm -f "$PROXYGEN_PRIVATE_KEY_FILE" "$PROXYGEN_CONFIG_FILE"

    # Clean up OAS backup file
    local backup_file="${OASPEC_FILE}.backup"
    if [[ -f "$backup_file" ]]; then
        rm -f "$backup_file"
        echo "Removed OAS backup file: $backup_file"
    fi
}

# Set up cleanup trap
trap cleanup EXIT

# Main execution flow
main() {
    echo "=== Phase 1: Dependency Check ==="
    check_dependencies

    echo -e "\n=== Phase 2: Retrieving Secrets ==="
    for i in "${!SECRETS[@]}"; do
        retrieve_secret "${SECRETS[$i]}" "${OUTPUT_VARS[$i]}"
    done

    echo -e "\n=== Phase 3: Retrieving Private Key from S3 ==="
    retrieve_private_key_from_s3

    echo -e "\n=== Phase 4: Preprocessing OpenAPI Specification ==="
    preprocess_oaspec

    echo -e "\n=== Phase 5: Validating OpenAPI Specification ==="
    validate_oaspec

    echo -e "\n=== Phase 7: Setting Proxygen CLI Credentials ==="
    setup_proxygen_auth

    echo -e "\n=== Phase 8: Deploying to Proxygen ==="
    deploy_to_proxygen

    echo -e "\n=== Phase 9: Verification ==="
    list_proxygen_deployments

    echo -e "\n🎉 Proxygen deployment process completed successfully!"
    echo "Proxy is now deployed and ready to handle requests."
}

# Run main function
main "$@"
