# Example Lambda Event Payloads

This directory contains example event payloads for testing Lambda functions locally.

## Reference Data Load Events

### Triage Code Load Event

**File**: `reference-data-load-triagecode.json`

**Purpose**: Triggers the loading of triage codes into the reference data tables.

**Event Structure**:

```json
{
  "type": "triagecode"
}
```

**Fields**:

- `type`: The type of reference data to load. Currently supports:
  - `"triagecode"`: Loads triage code reference data

---

## Queue Populator Events

### Full Sync Event

**File**: `queue-populator-full-sync.json`

**Purpose**: Triggers a full sync of services to the SQS queue based on type and status filters.

**Event Structure**:

```json
{
  "table_name": "services",
  "service_id": null,
  "record_id": null,
  "full_sync": true,
  "type_ids": [],
  "status_ids": []
}
```

**Fields**:

- `table_name`: The database table name (default: `"services"`)
- `service_id`: Service ID for single service sync (null for full sync)
- `record_id`: Record ID for single record sync (null for full sync)
- `full_sync`: Boolean is indicating whether to perform a full sync (true) or single record sync (false)
- `type_ids`: List of service type IDs to filter by (null to skip filter)
- `status_ids`: List of service status IDs to filter by (null to skip filter)

### Single Service Event

**File**: `queue-populator-single-service.json`

**Purpose**: Triggers a single service sync to the SQS queue.

**Event Structure**:

```json
{
  "table_name": "services",
  "service_id": 12345,
  "record_id": 12345,
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

**Fields**: Same as Full Sync Event, but with `full_sync` set to `false` and specific `service_id` and `record_id` provided.

---

## Running Lambda Functions Locally

### Running Reference Data Load Lambda

#### Method 1: Run with Python Directly

This method runs the Lambda handler function directly in Python without AWS tooling.

```bash
   # Activate Python virtual environment
   eval $(poetry env activate)

   # Set required environment variables
   export ENVIRONMENT=local
   export WORKSPACE=test_workspace
   export ENDPOINT_URL=http://localhost:8000

   # Run the Lambda handler with an example event
   python -c "
   from reference_data_load.lambda_handler import lambda_handler
   from aws_lambda_powertools.utilities.typing import LambdaContext

   event = {'type': 'triagecode'}
   context = LambdaContext()
   lambda_handler(event, context)
   "
```

### Running Queue Populator Lambda

#### Prerequisites

1. Ensure a local Postgres database is running with DoS data:
   ```bash
   cd services/data-migration
   mkdir -p ./.tmp/pg_data
   podman compose up -d
   ```

2. Ensure local SQS queue is available (using LocalStack or AWS):
   ```bash
   # For LocalStack
   docker run -d -p 4566:4566 localstack/localstack

   # Create a test queue
   aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name data-migration-queue
   ```

3. Set up environment variables:
   ```bash
   # Required: SQS Queue URL
   export SQS_QUEUE_URL=http://localhost:4566/data-migration-queue

   # Optional: Database connection (if not using AWS Secrets Manager)
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_USERNAME=postgres
   export DB_PASSWORD=postgres
   export DB_NAME=postgres
   ```


#### Run with Python Directly (Manual)

If you prefer to run the Lambda handler directly without the script:

```bash
   # Activate Python virtual environment
   cd services/data-migration
   eval $(poetry env activate)

   # Set required environment variables
   export SQS_QUEUE_URL=http://localhost:4566/data-migration-queue

   # Run with full sync event
   python -c "
   import json
   import sys
   sys.path.insert(0, 'src')
   from queue_populator.lambda_handler import lambda_handler
   from aws_lambda_powertools.utilities.typing import LambdaContext

   with open('events/queue-populator-full-sync.json') as f:
       event = json.load(f)
   lambda_handler(event, LambdaContext())
   "

   # Or run with single service event
   python -c "
   import json
   import sys
   sys.path.insert(0, 'src')
   from queue_populator.lambda_handler import lambda_handler
   from aws_lambda_powertools.utilities.typing import LambdaContext

   with open('events/queue-populator-single-service.json') as f:
       event = json.load(f)
   lambda_handler(event, LambdaContext())
   "
```


## Running Lambda Functions Locally (reference_data_load.lambda_handler)

### Run with Python Directly

This method runs the Lambda handler function directly in Python without AWS tooling.

```bash
   # Activate Python virtual environment
   eval $(poetry env activate)

   # Set required environment variables
   export ENVIRONMENT=local
   export WORKSPACE=test_workspace
   export ENDPOINT_URL=http://localhost:8000

   # Run the Lambda handler with an example event
   python -c "
   from reference_data_load.lambda_handler import lambda_handler
   from aws_lambda_powertools.utilities.typing import LambdaContext

   event = {'type': 'triagecode'}
   context = LambdaContext()
   lambda_handler(event, context)
   "
```
