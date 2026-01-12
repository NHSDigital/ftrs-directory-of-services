#!/usr/bin/env python3

import yaml
import json
import sys
import os
from datetime import datetime
from pathlib import Path


def load_toggle_registry(registry_file: str) -> dict:
    """Load and parse the toggle registry YAML file"""
    try:
        with open(registry_file, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(
            f"Error: Toggle registry file not found: {registry_file}", file=sys.stderr
        )
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing toggle registry YAML: {str(e)}", file=sys.stderr)
        sys.exit(1)


def validate_lifecycle(lifecycle: str) -> None:
    """Validate that lifecycle value is one of the allowed values"""
    valid_lifecycles = ["kill-switch", "temporary-rollout", "experiment"]
    if lifecycle not in valid_lifecycles:
        raise ValueError(
            f"Invalid lifecycle '{lifecycle}'. Must be one of: {', '.join(valid_lifecycles)}"
        )


def generate_appconfig_json(
    registry: dict, environment: str, created_date: str = None
) -> dict:
    """
    Generate AWS AppConfig Feature Flags JSON from the toggle registry.

    Args:
        registry: The parsed toggle registry dictionary
        environment: The environment to generate flags for (e.g., 'dev', 'test', 'prod')
        created_date: Optional ISO date string for created_at metadata

    Returns:
        Dictionary in AWS AppConfig Feature Flags format
    """
    if "appconfig_flags" not in registry:
        print(
            "Warning: No appconfig_flags section found in toggle registry",
            file=sys.stderr,
        )
        return {"version": "1", "flags": {}, "values": {}}

    appconfig_flags = registry["appconfig_flags"]

    # Initialize the AppConfig structure
    appconfig = {"version": "1", "flags": {}, "values": {}}

    # Use current date if not provided
    if created_date is None:
        created_date = datetime.now().isoformat()

    # Process each flag
    for flag in appconfig_flags:
        flag_id = flag.get("id")
        if not flag_id:
            print("Warning: Skipping flag without 'id' field", file=sys.stderr)
            continue

        # Validate required fields
        required_fields = ["name", "description", "owner", "lifecycle", "environments"]
        missing_fields = [field for field in required_fields if field not in flag]
        if missing_fields:
            print(
                f"Warning: Skipping flag '{flag_id}' - missing required fields: {', '.join(missing_fields)}",
                file=sys.stderr,
            )
            continue

        # Validate lifecycle
        try:
            validate_lifecycle(flag["lifecycle"])
        except ValueError as e:
            print(f"Warning: Skipping flag '{flag_id}' - {str(e)}", file=sys.stderr)
            continue

        # Add flag definition
        appconfig["flags"][flag_id] = {
            "name": flag["name"],
            "description": flag["description"],
            "_metadata": {
                "owner": flag["owner"],
                "created_at": created_date,
                "lifecycle": flag["lifecycle"],
            },
        }

        # Get enabled value for this environment
        environments = flag.get("environments", {})
        enabled = environments.get(environment, False)

        # Add flag value
        appconfig["values"][flag_id] = {"enabled": enabled}

        print(
            f"Processed flag '{flag_id}': enabled={enabled} for environment '{environment}'",
            file=sys.stderr,
        )

    return appconfig


def write_feature_flags_json(appconfig: dict, output_file: str) -> None:
    """Write the AppConfig JSON to the specified file"""
    try:
        # Ensure the output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the JSON file with proper formatting
        with open(output_file, "w") as f:
            json.dump(appconfig, f, indent=4)

        print(f"Feature flags JSON written to: {output_file}", file=sys.stderr)
        print(
            f"Generated {len(appconfig['flags'])} flags for deployment", file=sys.stderr
        )

    except IOError as e:
        print(f"Error writing feature flags JSON: {str(e)}", file=sys.stderr)
        sys.exit(1)


def generate_feature_flags(
    registry_file: str, environment: str, output_file: str, created_date: str = None
) -> str:
    """
    Main function to generate feature flags JSON.

    Args:
        registry_file: Path to the toggle registry YAML file
        environment: The environment to generate flags for
        output_file: Path where the feature flags JSON should be written
        created_date: Optional ISO date string for created_at metadata

    Returns:
        Path to the generated JSON file
    """
    try:
        print(f"Loading toggle registry from: {registry_file}", file=sys.stderr)
        print(
            f"Generating feature flags for environment: {environment}", file=sys.stderr
        )

        registry = load_toggle_registry(registry_file)
        appconfig = generate_appconfig_json(registry, environment, created_date)
        write_feature_flags_json(appconfig, output_file)

        return output_file

    except Exception as e:
        print(f"Error generating feature flags: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Read environment variables
    environment = os.environ.get("ENVIRONMENT")
    registry_file = os.environ.get("TOGGLE_REGISTRY_FILE")
    output_file = os.environ.get("OUTPUT_FILE")
    created_date = os.environ.get("CREATED_DATE")

    # Validate required environment variables
    if not environment:
        print("Error: ENVIRONMENT environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not registry_file:
        print(
            "Error: TOGGLE_REGISTRY_FILE environment variable is required",
            file=sys.stderr,
        )
        sys.exit(1)

    if not output_file:
        print("Error: OUTPUT_FILE environment variable is required", file=sys.stderr)
        sys.exit(1)

    # Generate the feature flags
    generated_file = generate_feature_flags(
        registry_file, environment, output_file, created_date
    )
    print(generated_file)
