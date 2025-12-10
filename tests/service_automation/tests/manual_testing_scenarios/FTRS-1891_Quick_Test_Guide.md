# FTRS-1891: Quick Test Guide - 3 Lambda Tests

## Quick test in 3 steps

**Lambda**: `ftrs-dos-dev-data-migration-queue-populator-lambda-ftrs-1898`
**Region**: eu-west-2
**Duration**: ~15 minutes

---

## Preparation

### 1. Find Service ID
```sql
-- Connect to ftrs-dos-dev
SELECT id FROM pathwaysdos.services WHERE statusid = 1 LIMIT 1;
-- Save ID: __________
```

### 2. Check SQS Queue
1. Open Lambda in AWS Console
2. Configuration → Environment variables → note `SQS_QUEUE_URL`
3. Open this queue in SQS Console
4. Note current message count: **__________**

---

## Test 1: Single Service ✅

### Event JSON
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
*(Replace 12345 with real ID from step 1)*

### Invoke Lambda
1. Lambda Console → **Test** tab
2. Create new event: `QuickTest1-SingleService`
3. Paste JSON (with real service_id)
4. **Test**

### Verification

- [ ] Status: **succeeded** (green)
- [ ] CloudWatch Logs: search for `"count": 1`
- [ ] SQS Queue: **+1 message**
- [ ] Poll messages → verify body contains `"service_id": 12345`

**Result**: ⬜ PASS / ⬜ FAIL

---

## Test 2: Full Sync (type=100, status=1) ✅

### Event JSON
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

### Check expected count

```sql
SELECT COUNT(*) FROM pathwaysdos.services
WHERE statusid = 1 AND typeid = 100;
-- Expected count: __________
```

### Invoke Lambda

1. Edit event or Create new: `QuickTest2-FullSync`
2. Paste JSON
3. **Test**

### Verification

- [ ] Status: **succeeded**
- [ ] CloudWatch Logs: `"count": __________` (matches SQL?)
- [ ] SQS Queue: **+X messages** (X = count from SQL)

**Result**: ⬜ PASS / ⬜ FAIL

---

## Test 3: Empty JSON ✅

### Event JSON

```json
{}
```

### Invoke Lambda

1. Edit event or Create new: `QuickTest3-EmptyJSON`
2. Paste empty JSON: `{}`
3. **Test**

### Verification

- [ ] Status: **failed** or error (expected error!)
- [ ] CloudWatch Logs contain error message (e.g. validation error, missing field)
- [ ] SQS Queue: **no new messages**

**Result**: ⬜ PASS / ⬜ FAIL

---

## Summary

| Test | Event | Expected Result | Actual Result |
|------|-------|-----------------|---------------|
| 1 | Single service | +1 message | |
| 2 | Full sync | +X messages | |
| 3 | Empty JSON | Error | |

### Success Criteria

- [ ] Test 1: 1 message in SQS with correct service_id
- [ ] Test 2: Number of messages = number of services from SQL
- [ ] Test 3: Lambda returns error, no messages in SQS

---

## Notes

**Service ID used**: __________
**Expected count (Test 2)**: __________
**Actual count (Test 2)**: __________
**Issues**: __________

---

**Tester**: __________
**Date**: __________
**Environment**: dev / ftrs-1898

---

## What's Next?

If all 3 tests PASS:

- ✅ Basic functionality works
- 📝 Document results in Jira FTRS-1891
- 🔍 Optional: full tests from `FTRS-1891_Manual_Testing_Plan.md`

If any test FAIL:

- 📸 Screenshot error message
- 📋 Copy CloudWatch Logs
- 🐛 Report bug to developer
