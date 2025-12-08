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

## Running Reference Lambda Functions Locally

### Method 1: Run with Python Directly

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
