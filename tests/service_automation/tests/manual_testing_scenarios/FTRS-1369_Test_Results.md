# FTRS-1369 Manual Testing Results
## Implement serviceendpoints change lambda trigger

**Tester:** [Your Name]
**Date:** 2025-12-08
**Environment:** Dev
**Database:** [DB Instance Name]

---

## Pre-Test Verification

### 1. Trigger Existence Check
**Query:** Check if triggers exist on `serviceendpoints` table

**Screenshot:** [Paste here]

**Result:**
- [ ] ✅ Trigger `serviceendpoints_lambda_notify_insert` exists
- [ ] ✅ Trigger `serviceendpoints_lambda_notify_update` exists
- [ ] ✅ Trigger `serviceendpoints_lambda_notify_delete` exists
- [ ] ✅ Function `related_service_change_notify()` exists

**Notes:**
```
[Add any observations]
```

---

## Test Data Identification

**Test Service ID:** 5752
**Test Service Name:** Abbey Medical Practice, Evesham, Worcestershire
**Service UID:** 138179

**Existing endpoints count:** _____

---

## TEST SCENARIO 1: INSERT

### Execution Details
**Timestamp:** [HH:MM:SS]
**SQL Executed:** ✅ / ❌

**Screenshot: SQL Execution**
[Paste here]

### Inserted Record Details
**New Endpoint ID:** _____________
**Service ID:** 5752
**Address:** https://test-ftrs-1369-insert.nhs.uk

**Screenshot: Record Verification**
[Paste here]

### Lambda Invocation Verification

#### Queue Populator Lambda (DMS Event Trigger)
**CloudWatch Log Group:** [Log group name]
**Timestamp:** [HH:MM:SS]

**Screenshot: Lambda Logs**
[Paste here]

**Payload Verification:**
```json
{
  "table_name": "serviceendpoints",
  "method": "INSERT",
  "service_id": "5752",
  "record_id": "[ACTUAL_ID]"
}
```

**Result:** ✅ / ❌

**Notes:**
```
[Any issues or observations]
```

#### SQS Queue
**Queue Name:** [Queue name]
**Message Received:** ✅ / ❌

**Screenshot: SQS Message**
[Paste here]

**Message Body:**
```json
[Paste actual message]
```

#### Service Migration Lambda (Processor)
**CloudWatch Log Group:** [Log group name]
**Timestamp:** [HH:MM:SS]

**Screenshot: Processor Logs**
[Paste here]

**Verification:**
- [ ] `sync_service(5752, 'update')` was called
- [ ] Service migration completed successfully
- [ ] No errors in logs

**Notes:**
```
[Any issues or observations]
```

### Target Database Verification
**Target DB checked:** ✅ / ❌

**Screenshot: Target DB Record**
[Paste here]

**Verification:**
- [ ] Service exists in target database
- [ ] Endpoint data matches source
- [ ] Migration timestamp updated

---

## TEST SCENARIO 2: UPDATE

### Execution Details
**Timestamp:** [HH:MM:SS]
**SQL Executed:** ✅ / ❌

**Screenshot: SQL Execution**
[Paste here]

### Updated Record Details
**Endpoint ID:** _____________
**New Address:** https://test-ftrs-1369-updated.nhs.uk
**New businessscenario:** FTRS-1369-UPDATE-TEST

**Screenshot: Record Verification**
[Paste here]

### Lambda Invocation Verification

#### Queue Populator Lambda
**Timestamp:** [HH:MM:SS]

**Screenshot: Lambda Logs**
[Paste here]

**Payload Verification:**
```json
{
  "table_name": "serviceendpoints",
  "method": "UPDATE",
  "service_id": "5752",
  "record_id": "[ACTUAL_ID]"
}
```

**Result:** ✅ / ❌

#### SQS Queue
**Message Received:** ✅ / ❌

**Screenshot: SQS Message**
[Paste here]

#### Service Migration Lambda
**Timestamp:** [HH:MM:SS]

**Screenshot: Processor Logs**
[Paste here]

**Verification:**
- [ ] `sync_service(5752, 'update')` was called
- [ ] Service update completed successfully
- [ ] No errors in logs

### Target Database Verification
**Screenshot: Updated Record**
[Paste here]

**Verification:**
- [ ] Updated endpoint data matches source
- [ ] Migration timestamp updated

---

## TEST SCENARIO 3: DELETE

### Execution Details
**Timestamp:** [HH:MM:SS]
**SQL Executed:** ✅ / ❌

**Screenshot: SQL Execution**
[Paste here]

### Deleted Record Details
**Endpoint ID:** _____________
**Service ID:** 5752

**Screenshot: Deletion Verification**
[Paste here]

**Verification:**
- [ ] Record deleted from source DB
- [ ] Count of test records = 0

### Lambda Invocation Verification

#### Queue Populator Lambda
**Timestamp:** [HH:MM:SS]

**Screenshot: Lambda Logs**
[Paste here]

**Payload Verification:**
```json
{
  "table_name": "serviceendpoints",
  "method": "DELETE",
  "service_id": "5752",
  "record_id": "[ACTUAL_ID]"
}
```

**Result:** ✅ / ❌

#### SQS Queue
**Message Received:** ✅ / ❌

**Screenshot: SQS Message**
[Paste here]

#### Service Migration Lambda
**Timestamp:** [HH:MM:SS]

**Screenshot: Processor Logs**
[Paste here]

**Verification:**
- [ ] `sync_service(5752, 'update')` was called
- [ ] Service sync completed successfully
- [ ] No errors in logs

### Target Database Verification
**Screenshot: Target DB State**
[Paste here]

**Verification:**
- [ ] Service still exists (DELETE endpoint doesn't delete service)
- [ ] Service was re-synced
- [ ] Migration timestamp updated

---

## Post-Test Cleanup

**Cleanup SQL Executed:** ✅ / ❌
**Remaining test records:** 0

**Screenshot: Cleanup Verification**
[Paste here]

---

## Overall Test Summary

### Acceptance Criteria Status

#### AC1: INSERT Scenario
- [ ] ✅ **PASSED** - Trigger invoked with correct payload
- [ ] ❌ **FAILED** - [Reason]
- [ ] ⚠️ **PARTIAL** - [Details]

#### AC2: UPDATE Scenario
- [ ] ✅ **PASSED** - Trigger invoked with correct payload
- [ ] ❌ **FAILED** - [Reason]
- [ ] ⚠️ **PARTIAL** - [Details]

#### AC3: DELETE Scenario (Not explicitly in ticket AC but tested)
- [ ] ✅ **PASSED** - Trigger invoked with correct payload
- [ ] ❌ **FAILED** - [Reason]
- [ ] ⚠️ **PARTIAL** - [Details]

### Issues Found

#### Critical Issues
1. [Issue description]
   - **Impact:** [High/Medium/Low]
   - **Screenshot:** [Paste here]
   - **Proposed fix:** [Description]

#### Minor Issues
1. [Issue description]

### Performance Observations
- Average Lambda invocation time: _____ ms
- Average SQS delivery time: _____ ms
- Average service migration time: _____ s

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

---

## Sign-off

**Tester:** _________________
**Date:** _________________

**Tech Lead Review:** _________________
**Date:** _________________

**QA Lead Review:** _________________
**Date:** _________________

---

## Additional Notes

```
[Any additional observations, edge cases discovered, or recommendations for future improvements]
```
