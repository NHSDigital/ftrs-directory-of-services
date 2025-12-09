# FTRS-1369 Test Report

**Tester:** Sylwia Luczak-Jagiela
**Date:** 9 December 2025
**Status:** ✅ PASSED

Verified that triggers on `serviceendpoints` table invoke Lambda and migrate data to DynamoDB successfully.

---

## Test Service: 45349
- Type: GP Practice (typeid=100)
- ODS: A12345, Status: Active
- Address: 123 Test Street, London, SW1A 1AA

---

## TEST 1: INSERT Endpoint

**SQL:**
```sql
INSERT INTO pathwaysdos.serviceendpoints
(id, serviceid, address, endpointorder, transport, format, interaction, businessscenario)
VALUES
(385014, 45349, 'https://test-ftrs-1369-insert-v3.nhs.uk', 1,
 'http', 'application/fhir', 'scheduling', 'Primary');
```

**Result:** ✅ Success - migrated to DynamoDB

**AWS CloudWatch Screenshots:**
- `screenshot_insert_01_pipeline_start.png` - "Starting Data Migration ETL Pipeline"
- `screenshot_insert_02_transformer.png` - "Transformer GPPracticeTransformer selected"
- `screenshot_insert_03_dynamodb.png` - "Item put into DynamoDB table" (3x)
- `screenshot_insert_04_success.png` - "Record successfully migrated"

**Timestamp:** 09:12:19-09:12:21 UTC
**RequestId:** 79bce5d8-8dd3-534e-8685-846967c0dbdc

---

## TEST 2: UPDATE Service

**SQL:**
```sql
UPDATE pathwaysdos.services
SET publicname = 'Test Service FTRS-1369 UPDATED',
    address = '123 Test Street',
    postcode = 'SW1A 1AA',
    town = 'London',
    publicphone = '01234567890',
    nonpublicphone = '01234567891',
    email = 'test@nhs.uk'
WHERE id = 45349;
```

**Result:** ✅ Success - triggered endpoint re-migration

**AWS CloudWatch Screenshots:**
- `screenshot_update_01_pipeline_start.png` - "Starting Data Migration ETL Pipeline"
- `screenshot_update_02_transformer.png` - "Transformer GPPracticeTransformer selected"
- `screenshot_update_03_success.png` - "Data Migration ETL Pipeline completed successfully"

**Timestamp:** 09:07:01-09:07:03 UTC
**RequestId:** 6ddef4ec-551a-5a92-a193-955dbdc4179e

---

## TEST 3: DELETE Endpoint (Negative Test)

**SQL:**
```sql
DELETE FROM pathwaysdos.serviceendpoints
WHERE id IN (385010, 385011, 385012);
```

**Result:** ✅ Correctly handled - DELETE not supported (logged as WARNING, ignored)

**AWS CloudWatch Screenshots:**
- `screenshot_delete_01_warning.png` - WARNING: "Unsupported event method: DELETE"
- `screenshot_delete_02_completed.png` - "Pipeline completed successfully" (no processing)

**Timestamp:** 08:59:07 UTC
**RequestId:** ffd7db29-9653-5b86-a4d2-ba9871525a37

---

## Validation Rules Confirmed

**Service Requirements:**
- typeid: 100/136/152, statusid: 1, valid ODS code
- Complete address (address, postcode, town)
- Contact details (phone, email)

**Endpoint Requirements:**
- transport: 'http' (lowercase!)
- format: 'application/fhir' or other valid MIME
- interaction: 'scheduling' or NHS ITK URN
- businessscenario: 'Primary' or 'Copy'

**Invalid values cause validation errors** (tested and confirmed)

---

## Conclusion

✅ **APPROVED** - Triggers work correctly
⚠️ **Note:** Deploy pending FTRS-1702 resolution (multiple invocations issue)
