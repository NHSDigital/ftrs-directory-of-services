#!/bin/bash

# Script to deploy API spec to Proxygen with workspace modifications
# Required environment variables: WORKSPACE, API_NAME, PROXY_ENV, ACCESS_TOKEN

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

if [ -z "$PROXY_ENV" ]; then
    echo "Error: PROXY_ENV environment variable is required" >&2
    exit 1
fi

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Error: ACCESS_TOKEN environment variable is required" >&2
    exit 1
fi

# Set the spec file path
SPEC_FILE="../../docs/specification/dos-search.yaml"

if [ ! -f "$SPEC_FILE" ]; then
    echo "Error: Spec file not found at $SPEC_FILE" >&2
    exit 1
fi

echo "Modifying OAS spec for workspace: $WORKSPACE" >&2

# Create Python script for modifying the spec
cat > /tmp/modify_spec.py << 'PYTHON_SCRIPT'
import yaml
import json
import sys
import os

def modify_spec(spec_file, workspace, api_name, environment):
    """Modify the OAS spec with workspace information and convert to JSON"""
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
        
        # Update servers to match Proxygen format requirements
        # Only update internal-dev server for internal-dev environment
        if 'servers' in spec and environment == 'internal-dev':
            for server in spec['servers']:
                if 'url' in server and 'internal-dev.api.service.nhs.uk' in server['url']:
                    # Extract existing path after the API name
                    # e.g., https://internal-dev.api.service.nhs.uk/dos-search/FHIR/R4
                    url_parts = server['url'].split('/')
                    if len(url_parts) >= 4:
                        # Get path segments after the API name (e.g., /FHIR/R4)
                        path_segments = '/'.join(url_parts[4:]) if len(url_parts) > 4 else ''
                        
                        # Build new URL with workspace
                        instance_name = f"{api_name}-{workspace.lower()}"
                        if path_segments:
                            server['url'] = f"https://internal-dev.api.service.nhs.uk/{instance_name}/{path_segments}"
                        else:
                            server['url'] = f"https://internal-dev.api.service.nhs.uk/{instance_name}"
                        
                        print(f"Updated internal-dev server URL to: {server['url']}", file=sys.stderr)
        
        # Write modified spec to temporary file as JSON
        output_file = '/tmp/modified_spec.json'
        with open(output_file, 'w') as f:
            json.dump(spec, f, indent=2)
        
        print(f"Modified spec written to {output_file}", file=sys.stderr)
        return output_file
        
    except Exception as e:
        print(f"Error modifying spec: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    workspace = os.environ.get('WORKSPACE')
    api_name = os.environ.get('API_NAME')
    spec_file = os.environ.get('SPEC_FILE')
    environment = os.environ.get('PROXY_ENV')
    
    modified_file = modify_spec(spec_file, workspace, api_name, environment)
    print(modified_file)
PYTHON_SCRIPT

# Modify the spec
echo "Processing specification file..." >&2
MODIFIED_SPEC=$(WORKSPACE="$WORKSPACE" API_NAME="$API_NAME" SPEC_FILE="$SPEC_FILE" PROXY_ENV="$PROXY_ENV" python3 /tmp/modify_spec.py)

if [ ! -f "$MODIFIED_SPEC" ]; then
    echo "Error: Failed to create modified spec" >&2
    rm -f /tmp/modify_spec.py
    exit 1
fi

echo "Modified spec created successfully as JSON" >&2

# Debug: Show the first server URL from the modified spec
echo "Checking modified server URLs..." >&2
python3 -c "import json; f=open('$MODIFIED_SPEC'); spec=json.load(f); print(f\"First server URL: {spec['servers'][0]['url']}\", file=__import__('sys').stderr)"

# Set Proxygen API URL
PROXYGEN_URL="https://proxygen.prod.api.platform.nhs.uk"

# Convert workspace to lowercase using tr
WORKSPACE_LOWER=$(echo "$WORKSPACE" | tr '[:upper:]' '[:lower:]')

# Set instance name based on environment
if [ "$PROXY_ENV" = "internal-dev" ]; then
    # For internal-dev, include the full path as instance name
    # e.g., dos-search-ftrs-000_FHIR_R4
    INSTANCE_NAME="${API_NAME}-${WORKSPACE_LOWER}_FHIR_R4"
else
    # For other environments, use just the API_NAME
    INSTANCE_NAME="${API_NAME}"
fi

echo "Debug: WORKSPACE=$WORKSPACE" >&2
echo "Debug: WORKSPACE_LOWER=$WORKSPACE_LOWER" >&2
echo "Debug: API_NAME=$API_NAME" >&2
echo "Debug: PROXY_ENV=$PROXY_ENV" >&2
echo "Using instance name: $INSTANCE_NAME" >&2

# Deploy to Proxygen using the environment/instance endpoint
echo "Deploying to Proxygen API..." >&2
echo "Endpoint: PUT ${PROXYGEN_URL}/apis/${API_NAME}/environments/${PROXY_ENV}/instances/${INSTANCE_NAME}" >&2

RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
    "${PROXYGEN_URL}/apis/${API_NAME}/environments/${PROXY_ENV}/instances/${INSTANCE_NAME}" \
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
    echo "✓ Successfully deployed API spec to Proxygen" >&2
    echo "$BODY"
    exit 0
elif [ "$HTTP_CODE" -eq 204 ]; then
    echo "✓ Successfully deployed API spec to Proxygen (no content returned)" >&2
    exit 0
else
    echo "Error: Failed to deploy API spec (HTTP $HTTP_CODE)" >&2
    echo "Response: $BODY" >&2
    exit 1
fi
