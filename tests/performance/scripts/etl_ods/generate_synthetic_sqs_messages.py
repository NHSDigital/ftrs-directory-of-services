"""Generate synthetic FHIR Organization messages and send to SQS transform queue.

Usage:
    ENVIRONMENT=dev python scripts/etl_ods/generate_synthetic_sqs_messages.py
    ENVIRONMENT=dev WORKSPACE=default COUNT=1000 python scripts/etl_ods/generate_synthetic_sqs_messages.py

Required:  ENVIRONMENT (dev|test|int|ref)
Optional:  WORKSPACE (default: "default"), COUNT (default: 100),
           AWS_REGION (default: eu-west-2),
           BATCH_SIZE (default: 10), DRY_RUN (default: false)

If parameter_files/crud_organisation_ids.csv exists, real ODS codes are used.
Otherwise synthetic PERF0001-style codes are generated.
Run 'make ds-data-prep' first to extract real ODS codes from DynamoDB.
"""

import csv
import json
import os
import sys
import uuid
from pathlib import Path

import boto3

SCRIPT_DIR = Path(__file__).resolve().parent
PERF_DIR = SCRIPT_DIR.parent.parent  # tests/performance/
CSV_PATH = PERF_DIR / "parameter_files" / "crud_organisation_ids.csv"


def load_ods_codes_from_csv(csv_path: Path) -> list[dict]:
    """Load organisation data from crud_organisation_ids.csv.

    Returns a list of dicts with keys: org_id, org_odscode, org_name.
    """
    rows: list[dict] = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def generate_ods_code(index: int) -> str:
    """Generate a synthetic ODS code like PERF0001."""
    return f"PERF{index:04d}"


def generate_organisation(
    index: int,
    ods_code: str | None = None,
    org_name: str | None = None,
) -> dict:
    """Generate a synthetic FHIR Organization resource.

    If ods_code is provided, uses it instead of generating a synthetic one.
    """
    org_id = str(uuid.uuid4())
    if ods_code is None:
        ods_code = generate_ods_code(index)
    if org_name is None:
        org_name = f"Performance Test Organisation {index}"

    return {
        "resourceType": "Organization",
        "id": org_id,
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "use": "official",
                "system": ("https://fhir.nhs.uk/Id/ods-organization-code"),
                "value": ods_code,
            }
        ],
        "active": True,
        "name": org_name,
        "type": [
            {
                "coding": [
                    {
                        "system": ("https://fhir.nhs.uk/CodeSystem/organisation-role"),
                        "code": "RO177",
                        "display": "PRESCRIBING COST CENTRE",
                    }
                ]
            }
        ],
        "telecom": [
            {"system": "phone", "value": "01234567890"}
        ],
        "address": [
            {
                "use": "work",
                "line": ["1 PERFORMANCE TEST STREET"],
                "city": "LONDON",
                "district": "GREATER LONDON",
                "postalCode": "SW1A 1AA",
                "country": "ENGLAND",
            }
        ],
        "extension": [
            {
                "url": (
                    "https://fhir.nhs.uk/England/"
                    "StructureDefinition/"
                    "Extension-England-OrganisationRole"
                ),
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": (
                                        "https://fhir.nhs.uk/"
                                        "CodeSystem/"
                                        "organisation-role"
                                    ),
                                    "code": "RO177",
                                    "display": ("PRESCRIBING COST CENTRE"),
                                }
                            ]
                        },
                    },
                    {
                        "url": "primaryRole",
                        "valueBoolean": True,
                    },
                    {
                        "url": "status",
                        "valueCoding": {
                            "system": (
                                "https://fhir.nhs.uk/"
                                "CodeSystem/"
                                "organisation-role-period-status"
                            ),
                            "code": "Active",
                        },
                    },
                ],
            }
        ],
    }


def get_queue_url(
    environment: str,
    workspace: str,
    region: str,
) -> str:
    """Look up the SQS transform queue URL."""
    sqs = boto3.client("sqs", region_name=region)
    workspace_suffix = f"-{workspace}" if workspace != "default" else ""
    queue_name = f"ftrs-dos-{environment}-etl-ods-transform-queue{workspace_suffix}"
    response = sqs.get_queue_url(QueueName=queue_name)
    return response["QueueUrl"]


def send_messages(
    queue_url: str,
    messages: list[dict],
    region: str,
    batch_size: int = 10,
) -> dict:
    """Send messages to SQS in batches of up to 10."""
    sqs = boto3.client("sqs", region_name=region)
    total_sent = 0
    total_failed = 0

    for i in range(0, len(messages), batch_size):
        batch = messages[i : i + batch_size]
        entries = [
            {
                "Id": str(idx),
                "MessageBody": json.dumps(msg),
            }
            for idx, msg in enumerate(batch)
        ]

        response = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)
        sent = len(response.get("Successful", []))
        failed = len(response.get("Failed", []))
        total_sent += sent
        total_failed += failed

        batch_num = i // batch_size + 1
        if failed > 0:
            print(f"  Batch {batch_num}: {sent} sent, {failed} failed")
            for fail in response.get("Failed", []):
                print(f"    Failed: {fail['Id']} - {fail['Message']}")
        else:
            print(f"  Batch {batch_num}: {sent} sent")

    return {"sent": total_sent, "failed": total_failed}


def main() -> None:
    """Generate and send synthetic messages to SQS."""
    environment = os.environ.get("ENVIRONMENT")
    if not environment:
        print("ERROR: ENVIRONMENT variable is required (dev|test|int|ref)")
        sys.exit(1)

    workspace = os.environ.get("WORKSPACE") or "default"
    region = os.environ.get("AWS_REGION") or "eu-west-2"
    count = int(os.environ.get("COUNT") or "100")
    batch_size = int(os.environ.get("BATCH_SIZE") or "10")
    dry_run = (os.environ.get("DRY_RUN") or "false").lower() == "true"

    print(f"Environment: {environment}")
    print(f"Workspace:   {workspace}")
    print(f"Region:      {region}")
    print(f"Count:       {count}")
    print(f"Dry run:     {dry_run}")
    print()

    # Load real ODS codes from CSV if available
    csv_rows: list[dict] = []
    if CSV_PATH.exists():
        csv_rows = load_ods_codes_from_csv(CSV_PATH)
        print(
            f"Loaded {len(csv_rows)} real ODS codes from "
            f"{CSV_PATH.name} (cycling if count > rows)"
        )
    else:
        print(
            f"No {CSV_PATH.name} found — using synthetic PERF codes. "
            f"Run 'make ds-data-prep' to use real ODS codes."
        )
    print()

    print(f"Generating {count} Organisation messages...")
    messages = []
    for i in range(count):
        if csv_rows:
            row = csv_rows[i % len(csv_rows)]
            organisation = generate_organisation(
                index=i + 1,
                ods_code=row.get("org_odscode", ""),
                org_name=row.get("org_name"),
            )
        else:
            organisation = generate_organisation(index=i + 1)

        messages.append({
            "organisation": organisation,
            "correlation_id": str(uuid.uuid4()),
            "request_id": str(uuid.uuid4()),
        })

    if dry_run:
        print("\nDRY RUN — sample message:")
        print(json.dumps(messages[0], indent=2))
        print(f"\nGenerated {len(messages)} messages (not sent)")
        return

    print("Looking up SQS queue...")
    queue_url = get_queue_url(environment, workspace, region)
    print(f"Queue URL: {queue_url}\n")

    print(f"Sending {count} messages in batches of {batch_size}...")
    result = send_messages(queue_url, messages, region, batch_size)
    print(f"\nDone: {result['sent']} sent, {result['failed']} failed")


if __name__ == "__main__":
    main()
