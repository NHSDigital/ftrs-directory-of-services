# FTRS-1702 Bug Report

**Reporter:** Sylwia Luczak-Jagiela
**Date:** 9 December 2025
**Severity:** High
**Environment:** Dev

---

## Issue

Lambda `ftrs-dos-dev-data-migration-rds-event-listener` invoked **~1000 times per single database operation** (INSERT/UPDATE).

**Impact:**
- Event duplication/loss
- RDS connection overload
- Performance degradation
- Increased costs

**Discovered during:** FTRS-1369 testing

---

## Evidence

### Test 1: Single INSERT (1 row)

**SQL:**
```sql
INSERT INTO pathwaysdos.serviceendpoints
(id, serviceid, address, endpointorder, transport, format, interaction, businessscenario)
VALUES
(385014, 45349, 'https://test-ftrs-1369-insert-v3.nhs.uk', 1,
 'http', 'application/fhir', 'scheduling', 'Primary');
```

**Expected:** 1 Lambda invocation
**Actual:** Multiple rapid invocations (exact count needs log analysis)

**Screenshot:** `screenshot_ftrs1702_insert_multiple_invocations.png`
**Timestamp:** 09:12:19-09:12:21 UTC

---

### Test 2: Single UPDATE (1 row)

**SQL:**
```sql
UPDATE pathwaysdos.services
SET publicname = 'Test Service FTRS-1369 UPDATED',
    address = '123 Test Street'
WHERE id = 45349;
```

**Expected:** 1 Lambda invocation
**Actual:** Multiple rapid invocations

**Screenshot:** `screenshot_ftrs1702_update_multiple_invocations.png`
**Timestamp:** 09:07:01-09:07:03 UTC

---

### Test 3: DELETE (3 rows)

**SQL:**
```sql
DELETE FROM pathwaysdos.serviceendpoints
WHERE id IN (385010, 385011, 385012);
```

**Expected:** 3 Lambda invocations
**Actual:** Multiple rapid invocations

**Screenshot:** `screenshot_ftrs1702_delete_multiple_invocations.png`
**Timestamp:** 08:59:07 UTC

---

## Root Cause (Hypothesis)

Possible causes:
1. Trigger configuration (incorrect timing/recursion)
2. Event fan-out (RDS/SQS duplication)
3. Lambda concurrency settings
4. Replication (triggers on primary + replica)

---

## Investigation Needed

1. CloudWatch log analysis - count exact invocations
2. Check database triggers for duplicates
3. Review Lambda event source mapping
4. Verify SQS queue configuration
5. Check RDS event subscriptions

---

## Impact

**Priority:** 🚨 High - **Blocks FTRS-1369 production deployment**

**Acceptance Criteria for Resolution:**
- ✅ 1 INSERT = exactly 1 Lambda invocation
- ✅ 1 UPDATE = exactly 1 Lambda invocation
- ✅ No duplicate events in DynamoDB
- ✅ Normal RDS connection count

---

## Test Data

**Service ID:** 45349
**CloudWatch Log Group:** `/aws/lambda/ftrs-dos-dev-data-migration-rds-event-listener`
**Test Date:** 9 December 2025, 08:00-10:00 UTC
