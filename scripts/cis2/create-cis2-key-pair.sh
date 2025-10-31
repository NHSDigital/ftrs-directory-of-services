#!/usr/bin/env bash

set -euo pipefail

# Script to create RSA 4096-bit key pair and store in AWS Secrets Manager
# The private key is stored in PEM format
# The public key is stored in JWKS format with a kid (key ID) that increments on each rotation

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 -r PROJECT_NAME -e ENVIRONMENT

Options:
    -r, --repo-name     Repository name
    -e, --environment   Environment (e.g., dev, int, test, prod)
    -h, --help          Display this help message

Example:
    $0 -r ftrs-directory-of-services -e dev
EOF
    exit 1
}

# Parse command line arguments
PROJECT_NAME=""
ENVIRONMENT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--repo-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate required parameters
if [[ -z "$PROJECT_NAME" ]] || [[ -z "$ENVIRONMENT" ]]; then
    log_error "Missing required parameters"
    usage
fi

log_info "Starting key pair generation for repo: $PROJECT_NAME, environment: $ENVIRONMENT"

# Define secret names
PRIVATE_KEY_SECRET_NAME="/${PROJECT_NAME}/${ENVIRONMENT}/cis2-private-key"
PUBLIC_KEY_SECRET_NAME="/${PROJECT_NAME}/${ENVIRONMENT}/cis2-public-key"

# Create temporary directory for key files
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

PRIVATE_KEY_FILE="$TEMP_DIR/private_key.pem"
PUBLIC_KEY_FILE="$TEMP_DIR/public_key.pem"
JWKS_FILE="$TEMP_DIR/public_key.jwks"

# Step 1: Generate RSA 4096-bit private key
log_info "Generating RSA 4096-bit private key..."
if openssl genrsa -out "$PRIVATE_KEY_FILE" 4096 2>/dev/null; then
    log_info "Private key generated successfully"
else
    log_error "Failed to generate private key"
    exit 1
fi

# Step 2: Extract public key in PEM format
log_info "Extracting public key in PEM format..."
if openssl rsa -in "$PRIVATE_KEY_FILE" -pubout -out "$PUBLIC_KEY_FILE" 2>/dev/null; then
    log_info "Public key extracted successfully"
else
    log_error "Failed to extract public key"
    exit 1
fi

# Step 3: Convert public key to JWKS format
log_info "Converting public key to JWKS format..."

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed. Please install it and rerun the script."
    exit 1
fi

# Determine the kid value by checking existing public key
log_info "Determining kid value..."
KID_NUMBER=1

# Try to get the existing public key from Secrets Manager
if aws secretsmanager describe-secret --secret-id "$PUBLIC_KEY_SECRET_NAME" &>/dev/null; then
    log_info "Found existing public key secret, extracting previous kid..."
    EXISTING_JWKS=$(aws secretsmanager get-secret-value --secret-id "$PUBLIC_KEY_SECRET_NAME" --query SecretString --output text 2>/dev/null || echo "")

    if [[ -n "$EXISTING_JWKS" ]]; then
        # Extract the kid value from the existing JWKS
        EXISTING_KID=$(echo "$EXISTING_JWKS" | jq -r '.keys[0].kid // empty' 2>/dev/null || echo "")

        if [[ -n "$EXISTING_KID" ]]; then
            log_info "Found existing kid: $EXISTING_KID"
            # Extract the number from the kid (format: environment-N)
            EXISTING_NUMBER=$(echo "$EXISTING_KID" | grep -oE '[0-9]+$' || echo "0")
            if [[ -n "$EXISTING_NUMBER" ]] && [[ "$EXISTING_NUMBER" =~ ^[0-9]+$ ]]; then
                KID_NUMBER=$((EXISTING_NUMBER + 1))
                log_info "Incrementing kid number from $EXISTING_NUMBER to $KID_NUMBER"
            else
                log_warning "Could not parse existing kid number, starting from 1"
            fi
        else
            log_info "No existing kid found, starting from 1"
        fi
    else
        log_info "No existing JWKS content found, starting from 1"
    fi
else
    log_info "No existing public key secret found, starting from 1"
fi

KID_VALUE="${ENVIRONMENT}-${KID_NUMBER}"
log_info "Using kid value: $KID_VALUE"

# Extract modulus (n) and exponent (e) from public key using openssl
PUBLIC_KEY_TEXT=$(openssl rsa -pubin -in "$PUBLIC_KEY_FILE" -text -noout 2>/dev/null)

if [[ $? -ne 0 ]]; then
    log_error "Failed to read public key"
    exit 1
fi

# Extract modulus (n) - remove "Modulus:" line and format
MODULUS_HEX=$(echo "$PUBLIC_KEY_TEXT" | sed -n '/^Modulus:/,/^Exponent:/p' | grep -v "Modulus:" | grep -v "Exponent:" | tr -d ' \n:')

# Extract exponent (e)
EXPONENT_DEC=$(echo "$PUBLIC_KEY_TEXT" | grep "^Exponent:" | awk '{print $2}')

# Convert hex modulus to base64url
# Remove leading zeros and convert to binary, then base64url encode
MODULUS_B64URL=$(echo "$MODULUS_HEX" | xxd -r -p | base64 | tr '+/' '-_' | tr -d '=')

# Convert decimal exponent to base64url
# Convert to hex, then to binary, then base64url encode
EXPONENT_HEX=$(printf '%x' "$EXPONENT_DEC")
# Pad hex to even length if needed
if [[ $((${#EXPONENT_HEX} % 2)) -eq 1 ]]; then
    EXPONENT_HEX="0${EXPONENT_HEX}"
fi
EXPONENT_B64URL=$(echo "$EXPONENT_HEX" | xxd -r -p | base64 | tr '+/' '-_' | tr -d '=')

# Create JWKS JSON using jq
jq -n \
    --arg n "$MODULUS_B64URL" \
    --arg e "$EXPONENT_B64URL" \
    --arg kid "$KID_VALUE" \
    '{
        keys: [
            {
                kty: "RSA",
                use: "sig",
                alg: "RS512",
                kid: $kid,
                n: $n,
                e: $e
            }
        ]
    }' > "$JWKS_FILE"

if [[ $? -eq 0 ]] && [[ -f "$JWKS_FILE" ]]; then
    log_info "Public key converted to JWKS format successfully"
else
    log_error "Failed to convert public key to JWKS format"
    exit 1
fi

# Step 4: Store private key in AWS Secrets Manager
log_info "Storing private key in AWS Secrets Manager..."
PRIVATE_KEY_CONTENT=$(cat "$PRIVATE_KEY_FILE")

# Check if secret exists
if aws secretsmanager describe-secret --secret-id "$PRIVATE_KEY_SECRET_NAME" &>/dev/null; then
    log_warning "Secret $PRIVATE_KEY_SECRET_NAME already exists, updating..."
    if aws secretsmanager update-secret \
        --secret-id "$PRIVATE_KEY_SECRET_NAME" \
        --secret-string "$PRIVATE_KEY_CONTENT" &>/dev/null; then
        log_info "Private key secret updated successfully"
    else
        log_error "Failed to update private key secret"
        exit 1
    fi
else
    log_error "Private key secret does not exist"
    exit 1
fi

# Step 5: Store public key (JWKS) in AWS Secrets Manager
log_info "Storing public key (JWKS) in AWS Secrets Manager..."
PUBLIC_KEY_CONTENT=$(cat "$JWKS_FILE")

# Check if secret exists
if aws secretsmanager describe-secret --secret-id "$PUBLIC_KEY_SECRET_NAME" &>/dev/null; then
    log_warning "Secret $PUBLIC_KEY_SECRET_NAME already exists, updating..."
    if aws secretsmanager update-secret \
        --secret-id "$PUBLIC_KEY_SECRET_NAME" \
        --secret-string "$PUBLIC_KEY_CONTENT" &>/dev/null; then
        log_info "Public key secret updated successfully"
    else
        log_error "Failed to update public key secret"
        exit 1
    fi
else
    log_error "Public key secret does not exist"
    exit 1
fi

log_info "========================================"
log_info "Key pair generation and storage complete!"
log_info "Private key stored in: $PRIVATE_KEY_SECRET_NAME"
log_info "Public key stored in: $PUBLIC_KEY_SECRET_NAME"
log_info "========================================"

exit 0
