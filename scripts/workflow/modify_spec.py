#!/usr/bin/env python3

import yaml
import json
import sys
import os


def load_spec_file(spec_file):
    """Load and parse the OAS spec file"""
    with open(spec_file, 'r') as f:
        return yaml.safe_load(f)


def update_spec_title(spec, workspace):
    """Update the spec title to include workspace information"""
    if workspace and 'info' in spec and 'title' in spec['info']:
        original_title = spec['info']['title']
        spec['info']['title'] = f"{workspace} {original_title}"


def update_target_url(spec, workspace):
    """Update x-nhsd-apim target URL to include workspace"""
    if workspace and 'x-nhsd-apim' in spec and 'target' in spec['x-nhsd-apim']:
        original_url = spec['x-nhsd-apim']['target']['url']
        # Insert workspace after the api name
        # e.g., https://dos-search.dev.ftrs.cloud.nhs.uk becomes
        # https://dos-search-ftrs-000.dev.ftrs.cloud.nhs.uk
        parts = original_url.replace('https://', '').split('.', 1)
        if len(parts) == 2:
            spec['x-nhsd-apim']['target']['url'] = f"https://{parts[0]}-{workspace}.{parts[1]}"


def get_environment_domain_map():
    """Return mapping of environments to API domains"""
    return {
        'internal-dev': 'internal-dev.api.service.nhs.uk',
        'internal-qa': 'internal-qa.api.service.nhs.uk',
        'int': 'int.api.service.nhs.uk',
        'ref': 'ref.api.service.nhs.uk',
        'prod': 'api.service.nhs.uk'
    }


def build_server_url(target_domain, api_name, workspace, environment, path_segments):
    """Build the server URL based on environment and workspace"""
    # If workspace is specified, deploy a workspaced instance
    if workspace:
        instance_name = f"{api_name}-{workspace}"
    else:
        instance_name = api_name

    if path_segments:
        return f"https://{target_domain}/{instance_name}/{path_segments}"
    else:
        return f"https://{target_domain}/{instance_name}"


def update_server_urls(spec, api_name, workspace, environment):
    """Update server URLs to match Proxygen format requirements"""
    if 'servers' not in spec:
        raise ValueError("Spec does not contain 'servers' section")

    env_domain_map = get_environment_domain_map()

    if environment not in env_domain_map:
        raise ValueError(f"Unknown environment: {environment}. Valid environments: {', '.join(env_domain_map.keys())}")

    target_domain = env_domain_map[environment]

    for server in spec['servers']:
        if 'url' not in server or target_domain not in server['url']:
            continue

        # Extract existing path after the API name
        # e.g., https://internal-dev.api.service.nhs.uk/dos-search/FHIR/R4
        url_parts = server['url'].split('/')
        if len(url_parts) < 4:
            continue

        # Get path segments after the API name (e.g., /FHIR/R4)
        path_segments = '/'.join(url_parts[4:]) if len(url_parts) > 4 else ''

        server['url'] = build_server_url(target_domain, api_name, workspace, environment, path_segments)
        print(f"Updated {environment} server URL to: {server['url']}", file=sys.stderr)


def write_spec_as_json(spec, output_file='/tmp/modified_spec.json'):
    """Write the modified spec to a JSON file"""
    with open(output_file, 'w') as f:
        json.dump(spec, f, indent=2)
    print(f"Modified spec written to {output_file}", file=sys.stderr)
    return output_file


def modify_spec(spec_file, workspace, api_name, environment):
    """Modify the OAS spec with workspace information and convert to JSON"""
    try:
        spec = load_spec_file(spec_file)
        update_spec_title(spec, workspace)
        update_target_url(spec, workspace)
        update_server_urls(spec, api_name, workspace, environment)
        return write_spec_as_json(spec)

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
