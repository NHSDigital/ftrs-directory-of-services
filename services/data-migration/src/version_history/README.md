# Version History Lambda Handler

Processes DynamoDB stream events to track version history for Organisation and Location records.

## Overview

- Listens to DynamoDB streams from Organisation and Location tables
- Extracts change data (old and new values)
- Stores version history in the version-history DynamoDB table
- Supports partial failure handling for batch processing

## Testing Locally

### Prerequisites

```bash
# Start local DynamoDB
cd services/data-migration
docker compose up -d

# Create tables (from ftrs_aws_local directory)
cd ../../application/packages/ftrs_aws_local
ftrs-aws-local reset --init --env local --endpoint-url http://localhost:8000

# Set environment variables (required)
export ENDPOINT_URL=http://localhost:8000
export ENVIRONMENT=local
export AWS_REGION=eu-west-2
```

### Run Unit Tests

```bash
cd services/data-migration
poetry run pytest tests/unit/version_history/ -v
```

### Run with Python Directly

```bash
cd services/data-migration
eval $(poetry env activate)

# Ensure environment variables are exported first
python -c "
import json
import sys
sys.path.insert(0, 'src')
from version_history.lambda_handler import lambda_handler
from unittest.mock import Mock

with open('src/version_history/version-history-stream-event.json') as f:
    event = json.load(f)

context = Mock()
context.function_name = 'test-version-history'
context.invoked_function_arn = 'arn:aws:lambda:eu-west-2:123456789:function:test'

result = lambda_handler(event, context)
print(f'Result: {result}')
"
```

**Success:** `Result: {'batchItemFailures': []}`

### Verify Results

```bash
# Scan version history table
aws dynamodb scan \
    --table-name ftrs-dos-local-database-version-history \
    --endpoint-url http://localhost:8000 \
    --region eu-west-2
```

## Troubleshooting

**ResourceNotFoundException error?**

1. Export environment variables before running Python (must be set first)
2. Verify table exists: `aws dynamodb list-tables --endpoint-url http://localhost:8000 --region eu-west-2`
3. Create tables if missing: `ftrs-aws-local reset --init --env local --endpoint-url http://localhost:8000`

## Environment Variables

- `ENDPOINT_URL` - DynamoDB endpoint URL (required for local testing)
- `ENVIRONMENT` - Environment name (`local`, `dev`)
- `AWS_REGION` - AWS region (default: `eu-west-2`)

## Files

- `lambda_handler.py` - Lambda entry point
- `stream_processor.py` - Stream record processor
- `version-history-stream-event.json` - Sample test event
- `../../tests/unit/version_history/` - Unit tests
