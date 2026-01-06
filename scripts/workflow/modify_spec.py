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


def get_environment_target_domain_map():
    """Return mapping of environments to target backend domains"""
    return {
        'internal-dev': 'dev.ftrs.cloud.nhs.uk',
        'internal-qa': 'test.ftrs.cloud.nhs.uk',
        'int': 'int.ftrs.cloud.nhs.uk',
        'ref': 'ref.ftrs.cloud.nhs.uk',
        'prod': 'prod.ftrs.cloud.nhs.uk'
    }


def update_target_url(spec, workspace, environment):
    """Update x-nhsd-apim target URL based on environment and workspace"""
    if 'x-nhsd-apim' not in spec or 'target' not in spec['x-nhsd-apim']:
        return

    original_url = spec['x-nhsd-apim']['target']['url']

    # Get the environment-specific target domain
    env_target_map = get_environment_target_domain_map()

    if environment and environment in env_target_map:
        target_domain = env_target_map[environment]

        # Extract the service name from the original URL
        # e.g., from https://dos-search.dev.ftrs.cloud.nhs.uk get 'dos-search'
        # or from https://crud.dev.ftrs.cloud.nhs.uk get 'crud'
        parts = original_url.replace('https://', '').split('.', 1)
        if len(parts) == 2:
            service_name = parts[0]

            # If workspace is specified, append it to the service name
            if workspace:
                service_name = f"{service_name}-{workspace}"

            # Build the new URL with the environment-specific domain
            new_url = f"https://{service_name}.{target_domain}"
            spec['x-nhsd-apim']['target']['url'] = new_url
            print(f"Updated target URL to: {new_url}", file=sys.stderr)
    elif workspace:
        # If no environment mapping but workspace is specified, just add workspace
        parts = original_url.replace('https://', '').split('.', 1)
        if len(parts) == 2:
            spec['x-nhsd-apim']['target']['url'] = f"https://{parts[0]}-{workspace}.{parts[1]}"
            print(f"Updated target URL with workspace: {spec['x-nhsd-apim']['target']['url']}", file=sys.stderr)


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

    # Track if we updated any servers
    updated_count = 0

    for server in spec['servers']:
        if 'url' not in server:
            continue

        # Check if this server URL is for an NHS API service domain
        # e.g., https://internal-dev.api.service.nhs.uk/dos-search/FHIR/R4
        url_parts = server['url'].split('/')
        if len(url_parts) < 5:  # Must have protocol, empty, domain, api_name, and path
            continue

        # Check if URL matches NHS API service pattern
        domain = url_parts[2]
        if 'api.service.nhs.uk' not in domain:
            continue

        # Get path segments after the API name (e.g., /FHIR/R4)
        path_segments = '/'.join(url_parts[4:]) if len(url_parts) > 4 else ''

        # Update this server URL to use the target environment domain
        server['url'] = build_server_url(target_domain, api_name, workspace, environment, path_segments)
        print(f"Updated server URL to: {server['url']}", file=sys.stderr)
        updated_count += 1

    if updated_count == 0:
        print(f"Warning: No server URLs were updated for environment {environment}", file=sys.stderr)


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
        update_target_url(spec, workspace, environment)
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
