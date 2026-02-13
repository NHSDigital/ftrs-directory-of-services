#!/usr/bin/env python3
"""Local testing script for version history functionality."""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime

import boto3
from rich.console import Console
from rich.table import Table

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from application.packages.ftrs_aws_local.dynamodb.reset import (
    ClearableEntityTypes,
    init_tables,
)
from application.packages.ftrs_aws_local.dynamodb.utils import TargetEnvironment

from version_history.lambda_handler import lambda_handler

console = Console()


def setup_environment(env: str, workspace: str | None, endpoint_url: str) -> None:
    """Set up environment variables."""
    os.environ["ENVIRONMENT"] = env
    os.environ["WORKSPACE"] = workspace or ""
    os.environ["ENDPOINT_URL"] = endpoint_url
    os.environ["PROJECT_NAME"] = "ftrs-dos"


def create_test_tables(endpoint_url: str) -> None:
    """Create test tables for organisations."""
    client = boto3.client("dynamodb", endpoint_url=endpoint_url)

    # Create organisation table
    try:
        client.create_table(
            TableName="organisation",
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
            StreamSpecification={
                "StreamEnabled": True,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
        )
        console.print("[green]Created organisation table[/green]")
    except client.exceptions.ResourceInUseException:
        console.print("[yellow]Organisation table already exists[/yellow]")


def create_organisation_record(endpoint_url: str, org_id: str) -> dict:
    """Create a test organisation record."""
    dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
    table = dynamodb.Table("organisation")

    record = {
        "id": org_id,
        "field": "document",
        "name": "Test Organisation",
        "email": "old@example.com",
        "status": "pending",
        "active": True,
        "createdTime": datetime.utcnow().isoformat(),
        "lastUpdated": datetime.utcnow().isoformat(),
        "createdBy": {
            "display": "Test User",
            "type": "user",
            "value": "test-user-123",
        },
        "lastUpdatedBy": {
            "display": "Test User",
            "type": "user",
            "value": "test-user-123",
        },
    }

    table.put_item(Item=record)
    console.print(f"[green]Created organisation record: {org_id}[/green]")
    return record


def update_organisation_record(
    endpoint_url: str, org_id: str, old_record: dict
) -> dict:
    """Update the organisation record."""
    dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
    table = dynamodb.Table("organisation")

    updated_record = old_record.copy()
    updated_record["email"] = "new@example.com"
    updated_record["status"] = "active"
    updated_record["lastUpdated"] = datetime.utcnow().isoformat()
    updated_record["lastUpdatedBy"] = {
        "display": "Test User Updated",
        "type": "user",
        "value": "test-user-456",
    }

    table.put_item(Item=updated_record)
    console.print(f"[green]Updated organisation record: {org_id}[/green]")
    return updated_record


def create_stream_event(org_id: str, old_record: dict, new_record: dict) -> dict:
    """Create a DynamoDB stream event."""
    from boto3.dynamodb.types import TypeSerializer

    serializer = TypeSerializer()

    # Serialize records to DynamoDB JSON format
    old_image = {key: serializer.serialize(value) for key, value in old_record.items()}
    new_image = {key: serializer.serialize(value) for key, value in new_record.items()}

    event = {
        "Records": [
            {
                "eventID": str(uuid.uuid4()),
                "eventName": "MODIFY",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "eu-west-2",
                "dynamodb": {
                    "ApproximateCreationDateTime": datetime.utcnow().timestamp(),
                    "Keys": {"id": {"S": org_id}, "field": {"S": "document"}},
                    "NewImage": new_image,
                    "OldImage": old_image,
                    "SequenceNumber": "123456789",
                    "SizeBytes": 1000,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
                "eventSourceARN": f"arn:aws:dynamodb:eu-west-2:123456789012:table/organisation/stream/2024-01-01T00:00:00.000",
            }
        ]
    }

    return event


def verify_version_history(endpoint_url: str, org_id: str) -> None:
    """Verify version history records were created."""
    dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
    table = dynamodb.Table("version-history")

    entity_id = f"organisation|{org_id}|document"

    response = table.query(
        KeyConditionExpression="entity_id = :entity_id",
        ExpressionAttributeValues={":entity_id": entity_id},
    )

    items = response.get("Items", [])

    if not items:
        console.print("[red]No version history records found![/red]")
        return

    console.print(f"[green]Found {len(items)} version history record(s)[/green]\n")

    for item in items:
        result_table = Table(title="Version History Record")
        result_table.add_column("Field", style="cyan")
        result_table.add_column("Value", style="magenta")

        result_table.add_row("Entity ID", item["entity_id"])
        result_table.add_row("Timestamp", item["timestamp"])
        result_table.add_row("Change Type", item["change_type"])
        result_table.add_row(
            "Changed Fields", json.dumps(item["changed_fields"], indent=2)
        )
        result_table.add_row("Changed By", json.dumps(item["changed_by"], indent=2))

        console.print(result_table)
        console.print()


def main() -> None:
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test version history locally")
    parser.add_argument("--env", default="local", help="Environment (default: local)")
    parser.add_argument("--workspace", default=None, help="Workspace")
    parser.add_argument(
        "--endpoint-url",
        default="http://localhost:8000",
        help="DynamoDB endpoint URL",
    )
    args = parser.parse_args()

    console.print("[bold blue]Version History Local Test[/bold blue]\n")

    # Setup environment
    setup_environment(args.env, args.workspace, args.endpoint_url)

    # Create tables
    console.print("[bold]Step 1: Creating tables...[/bold]")
    create_test_tables(args.endpoint_url)
    # Use centralized ftrs_aws_local table creation
    target_env = TargetEnvironment(args.env)
    init_tables(
        endpoint_url=args.endpoint_url,
        env=target_env,
        workspace=args.workspace,
        entity_type=[ClearableEntityTypes.version_history],
    )
    console.print()

    # Create organisation record
    console.print("[bold]Step 2: Creating organisation record...[/bold]")
    org_id = str(uuid.uuid4())
    old_record = create_organisation_record(args.endpoint_url, org_id)
    console.print()

    # Update organisation record
    console.print("[bold]Step 3: Updating organisation record...[/bold]")
    new_record = update_organisation_record(args.endpoint_url, org_id, old_record)
    console.print()

    # Create stream event
    console.print("[bold]Step 4: Creating stream event...[/bold]")
    stream_event = create_stream_event(org_id, old_record, new_record)
    console.print("[green]Stream event created[/green]")
    console.print()

    # Invoke lambda handler
    console.print("[bold]Step 5: Invoking lambda handler...[/bold]")
    result = lambda_handler(stream_event, {})
    console.print(f"Lambda result: {json.dumps(result, indent=2)}")
    console.print()

    # Verify version history
    console.print("[bold]Step 6: Verifying version history...[/bold]")
    verify_version_history(args.endpoint_url, org_id)

    console.print("[bold green]✓ Test completed successfully![/bold green]")


if __name__ == "__main__":
    main()
