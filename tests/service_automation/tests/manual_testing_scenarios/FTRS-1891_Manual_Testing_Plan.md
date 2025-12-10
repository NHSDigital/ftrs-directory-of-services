# FTRS-1891: Manual Testing Plan - Single Service Queue Populator

## Test Overview
**Feature**: Enable Single-Service Testing for Queue Populator Lambda
**Lambda Name**: `ftrs-dos-dev-data-migration-queue-populator-lambda-ftrs-1898`
**Workspace**: `ftrs-1898`
**Environment**: `dev`
**AWS Region**: `eu-west-2`

## Background
The queue populator Lambda previously only supported full sync operations, which required processing all services matching specific type_ids and status_ids. This made it difficult to test individual services without running a full migration. FTRS-1891 adds the capability to trigger the queue populator for a single service.

## Event Types

### 1. Single Service Event (NEW FUNCTIONALITY)
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

### 2. Full Sync Event (EXISTING FUNCTIONALITY)
```json
{
  "status_ids": [1],
  "type_ids": [100],
  "full_sync": true,
  "record_id": null,
  "service_id": null,
  "table_name": "services"
}
```

## Test Scenarios

### Test 1: Single Service Event - Valid Service ID
**Objective**: Verify that queue populator correctly processes a single service event

**Preconditions**:
- Service exists in `pathwaysdos.services` table
- Lambda has permissions to access database and SQS queue
- SQS queue is empty or in known state

**Test Data**:
- Service ID: Choose an active service from the database (e.g., 12345)

**Event Payload**:
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

**Expected Results**:
1. Lambda executes successfully (status code 200)
2. Exactly ONE message is added to SQS queue
3. SQS message contains DMSEvent with:
   - `type`: "dms_event"
   - `service_id`: 12345
   - `record_id`: 12345
   - `table_name`: "services"
   - `method`: "insert"
4. CloudWatch Logs show:
   - Log entry DM_QP_000: "Starting Data Migration Queue Populator"
   - Log entry DM_QP_001: "count": 1 (single service)
   - Log entry DM_QP_999: "Data Migration Queue Populator completed"
5. No errors in CloudWatch Logs

**Verification Steps**:
- Check SQS queue message count
- Inspect SQS message body
- Review CloudWatch Logs for Lambda execution
- Verify no DLQ (Dead Letter Queue) messages

---

### Test 2: Single Service Event - Non-Existent Service ID
**Objective**: Verify graceful handling of non-existent service

**Preconditions**:
- Service ID does NOT exist in database (e.g., 999999999)

**Test Data**:
- Service ID: 999999999 (non-existent)

**Event Payload**:
```json
{
  "table_name": "services",
  "service_id": 999999999,
  "record_id": 999999999,
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

**Expected Results**:
1. Lambda executes successfully (status code 200)
2. ZERO messages added to SQS queue (service not found)
3. CloudWatch Logs show:
   - Log entry DM_QP_000: "Starting Data Migration Queue Populator"
   - Log entry DM_QP_001: "count": 0 (no services found)
   - Log entry DM_QP_999: "Data Migration Queue Populator completed"
4. No errors or exceptions

**Verification Steps**:
- Check SQS queue message count remains unchanged
- Review CloudWatch Logs confirming 0 services processed

---

### Test 3: Single Service Event - Missing Required Parameters
**Objective**: Verify validation of required parameters

**Test Data**:
Multiple invalid payloads to test

**Event Payload 3a** (missing service_id):
```json
{
  "table_name": "services",
  "record_id": 12345,
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

**Event Payload 3b** (missing record_id):
```json
{
  "table_name": "services",
  "service_id": 12345,
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

**Event Payload 3c** (missing table_name):
```json
{
  "service_id": 12345,
  "record_id": 12345,
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

**Expected Results**:
1. Lambda fails with validation error
2. CloudWatch Logs show error message indicating missing required field
3. No messages added to SQS queue
4. Error message should clearly identify which parameter is missing

**Verification Steps**:
- Check Lambda execution status (should show error)
- Review CloudWatch Logs for validation error details
- Confirm SQS queue unchanged

---

### Test 4: Full Sync Event - Verify Backward Compatibility
**Objective**: Ensure existing full sync functionality still works after FTRS-1891 changes

**Preconditions**:
- Multiple services exist with status_id = 1 and type_id = 100

**Test Data**:
- status_ids: [1]
- type_ids: [100]

**Event Payload**:
```json
{
  "status_ids": [1],
  "type_ids": [100],
  "full_sync": true,
  "record_id": null,
  "service_id": null,
  "table_name": "services"
}
```

**Expected Results**:
1. Lambda executes successfully
2. Multiple messages added to SQS queue (one per matching service)
3. Number of messages matches count of services with status_id=1 AND type_id=100
4. CloudWatch Logs show:
   - Log entry DM_QP_000 with type_ids and status_ids
   - Log entry DM_QP_001 with count > 1
   - Log entry DM_QP_999
5. Each SQS message contains correct DMSEvent structure

**Verification Steps**:
- Count services in database matching criteria
- Compare with SQS message count
- Inspect sample SQS messages for correct format
- Review CloudWatch Logs

---

### Test 5: Single Service Event - Multiple Sequential Invocations
**Objective**: Verify Lambda can handle multiple single-service events sequentially

**Preconditions**:
- Three different valid service IDs exist (e.g., 12345, 12346, 12347)

**Test Data**:
- Service IDs: 12345, 12346, 12347

**Test Steps**:
1. Invoke Lambda with service_id=12345
2. Wait for completion
3. Invoke Lambda with service_id=12346
4. Wait for completion
5. Invoke Lambda with service_id=12347
6. Wait for completion

**Expected Results**:
1. Each Lambda invocation succeeds independently
2. Total of 3 messages in SQS queue
3. Each message corresponds to correct service_id
4. No interference between invocations
5. CloudWatch Logs show three separate execution cycles

**Verification Steps**:
- Monitor SQS queue after each invocation
- Verify message bodies match expected service_ids
- Check CloudWatch Logs for separate execution traces

---

### Test 6: Full Sync Event with Empty Result Set
**Objective**: Verify graceful handling when no services match criteria

**Preconditions**:
- NO services exist with status_id = 999 and type_id = 999

**Test Data**:
- status_ids: [999]
- type_ids: [999]

**Event Payload**:
```json
{
  "status_ids": [999],
  "type_ids": [999],
  "full_sync": true,
  "record_id": null,
  "service_id": null,
  "table_name": "services"
}
```

**Expected Results**:
1. Lambda executes successfully
2. ZERO messages added to SQS queue
3. CloudWatch Logs show:
   - Log entry DM_QP_000
   - Log entry DM_QP_001: "count": 0
   - Log entry DM_QP_999
4. No errors

**Verification Steps**:
- Verify SQS queue remains empty
- Review CloudWatch Logs confirming 0 services processed

---

## Verification Checklist

For each test, verify:

- [ ] Lambda execution status (Success/Failure)
- [ ] SQS queue message count matches expected
- [ ] SQS message structure is correct (DMSEvent format)
- [ ] CloudWatch Logs contain expected log entries (DM_QP_000, DM_QP_001, DM_QP_999)
- [ ] No unexpected errors or exceptions
- [ ] No messages in Dead Letter Queue (DLQ)
- [ ] Lambda execution time is reasonable
- [ ] No database connection issues

## Resources Needed

1. **AWS Console Access**:
   - Lambda console (to invoke function)
   - SQS console (to inspect queue)
   - CloudWatch Logs (to review execution logs)

2. **Database Access**:
   - Connection to `ftrs-dos-dev` database
   - Ability to query `pathwaysdos.services` table

3. **Test Data**:
   - Valid service IDs from database
   - Invalid/non-existent service IDs for negative testing

## Test Environment

- **AWS Account**: dev
- **Region**: eu-west-2
- **Lambda**: ftrs-dos-dev-data-migration-queue-populator-lambda-ftrs-1898
- **Workspace**: ftrs-1898
- **Database**: ftrs-dos-dev.pathwaysdos
- **SQS Queue**: [Queue URL from Lambda environment variables]

## Success Criteria

- All 6 test scenarios pass
- Single service events correctly populate queue with exactly 1 message
- Full sync events maintain backward compatibility
- Error handling is graceful for invalid inputs
- No regressions in existing functionality
- CloudWatch Logs provide clear audit trail

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Testing impacts production data | Use dev environment only, verify workspace=ftrs-1898 |
| SQS queue fills with test messages | Clear queue before/after testing |
| Lambda timeout with large full sync | Use type_ids/status_ids that return manageable dataset |
| Database connection issues | Verify Lambda has correct VPC/security group configuration |

## Notes

- Queue populator creates DMSEvent messages with `method="insert"` regardless of actual operation
- The queue populator does NOT perform the actual data migration - it only populates the queue
- Actual migration is performed by the processor Lambda that consumes from the queue
- For full testing of the migration flow, verify that processor Lambda correctly handles the queued messages

