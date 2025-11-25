#!/bin/bash

# Script to modify OAS spec with workspace information
# Required environment variables: WORKSPACE, API_NAME, PROXY_ENV
# Outputs the path to the modified spec file to stdout

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

# Set the spec file path (relative to repository root)
SPEC_FILE="docs/specification/dos-search.yaml"

if [ ! -f "$SPEC_FILE" ]; then
    echo "Error: Spec file not found at $SPEC_FILE" >&2
    echo "Current directory: $(pwd)" >&2
    echo "Looking for file at: $(realpath $SPEC_FILE 2>/dev/null || echo $SPEC_FILE)" >&2
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
                spec['x-nhsd-apim']['target']['url'] = f"https://{parts[0]}-{workspace}.{parts[1]}"

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
                        instance_name = f"{api_name}-{workspace}"
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

# Clean up Python script
rm -f /tmp/modify_spec.py

# Output the path to the modified spec file to stdout
echo "$MODIFIED_SPEC"
