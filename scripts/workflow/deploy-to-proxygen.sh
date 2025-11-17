#!/bin/bash

# Script to deploy API spec to Proxygen with workspace modifications
# Required environment variables: WORKSPACE, API_NAME, ENV, AWS_REGION, ACCESS_TOKEN

set -e

# Validate required environment variables
if [ -z "$WORKSPACE" ]; then
    echo "Error: WORKSPACE environment variable is required" >&2
    exit 1
fi

if [ -z "$API_NAME" ]; then
    echo "Error: API_NAME environment variable is required" >&2
    exit 1
fi

if [ -z "$ENV" ]; then
    echo "Error: ENV environment variable is required" >&2
    exit 1
fi

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Error: ACCESS_TOKEN environment variable is required" >&2
    exit 1
fi

# Set the spec file path
SPEC_FILE="specification/dos-search.yaml"

if [ ! -f "$SPEC_FILE" ]; then
    echo "Error: Spec file not found at $SPEC_FILE" >&2
    exit 1
fi

echo "Modifying OAS spec for workspace: $WORKSPACE" >&2

# Create Python script for modifying the spec
cat > /tmp/modify_spec.py << 'PYTHON_SCRIPT'
import yaml
import sys
import os

def modify_spec(spec_file, workspace, api_name):
    """Modify the OAS spec with workspace information"""
    try:
        with open(spec_file, 'r') as f:
            spec = yaml.safe_load(f)

        # Update title to include workspace
        original_title = spec['info']['title']
        spec['info']['title'] = f"{workspace} {original_title}"

        # Update x-nhsd-apim target URL to include workspace
        if 'x-nhsd-apim' in spec and 'target' in spec['x-nhsd-apim']:
            original_url = spec['x-nhsd-apim']['target']['url']
            # Insert workspace after the api name
            # e.g., https://dos-search.dev.ftrs.cloud.nhs.uk becomes
            # https://dos-search-ftrs-000.dev.ftrs.cloud.nhs.uk
            parts = original_url.replace('https://', '').split('.', 1)
            if len(parts) == 2:
                spec['x-nhsd-apim']['target']['url'] = f"https://{parts[0]}-{workspace.lower()}.{parts[1]}"

        # Write modified spec to temporary file
        output_file = '/tmp/modified_spec.yaml'
        with open(output_file, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        print(f"Modified spec written to {output_file}", file=sys.stderr)
        return output_file

    except Exception as e:
        print(f"Error modifying spec: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    workspace = os.environ.get('WORKSPACE')
    api_name = os.environ.get('API_NAME')
    spec_file = os.environ.get('SPEC_FILE')

    modified_file = modify_spec(spec_file, workspace, api_name)
    print(modified_file)
PYTHON_SCRIPT

# Modify the spec
echo "Processing specification file..." >&2
MODIFIED_SPEC=$(WORKSPACE="$WORKSPACE" API_NAME="$API_NAME" SPEC_FILE="$SPEC_FILE" python3 /tmp/modify_spec.py)

if [ ! -f "$MODIFIED_SPEC" ]; then
    echo "Error: Failed to create modified spec" >&2
    rm -f /tmp/modify_spec.py
    exit 1
fi

echo "Modified spec created successfully" >&2

# Determine Proxygen API URL based on environment
case "$ENV" in
    dev|test|int)
        PROXYGEN_URL="https://proxygen.prod.api.platform.nhs.uk"
        ;;
    prod)
        PROXYGEN_URL="https://proxygen.prod.api.platform.nhs.uk"
        ;;
    *)
        echo "Error: Unknown environment: $ENV" >&2
        rm -f /tmp/modify_spec.py "$MODIFIED_SPEC"
        exit 1
        ;;
esac

# Deploy to Proxygen
echo "Deploying to Proxygen API..." >&2
RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
    "${PROXYGEN_URL}/apis/${API_NAME}" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d @"$MODIFIED_SPEC")

# Extract HTTP status code and response body
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

# Clean up temporary files
rm -f /tmp/modify_spec.py "$MODIFIED_SPEC"

# Check response
if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
    echo "âœ" Successfully deployed API spec to Proxygen" >&2
    echo "$BODY"
    exit 0
elif [ "$HTTP_CODE" -eq 204 ]; then
    echo "âœ" Successfully deployed API spec to Proxygen (no content returned)" >&2
    exit 0
else
    echo "Error: Failed to deploy API spec (HTTP $HTTP_CODE)" >&2
    echo "Response: $BODY" >&2
    exit 1
fi
