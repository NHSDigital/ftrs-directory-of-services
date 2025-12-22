-- ============================================================================
-- MANUAL TEST SCRIPT FOR FTRS-1369: serviceendpoints trigger testing
-- ============================================================================
-- Author: Manual Testing
-- Date: 2025-12-09
-- Purpose: Test serviceendpoints table triggers and data migration pipeline
--
-- Prerequisites:
-- 1. Access to dev database where trigger is deployed
-- 2. Ability to monitor Lambda logs (CloudWatch)
-- 3. Understanding of GP Practice data requirements
--
-- Key Learnings from Testing:
-- - Service MUST have valid ODS code (6 chars: [ABCDEFGHJKLMNPVWY][0-9]{5})
-- - Service MUST have statusid = 1 (Active)
-- - Service MUST have complete address (address, postcode, town)
-- - Service MUST have contact details (publicphone, nonpublicphone, email)
-- - Endpoints MUST use lowercase 'http' (not 'HTTP')
-- - Endpoints format MUST be valid MIME type (e.g., 'application/fhir')
-- - Endpoints interaction MUST be valid URN or 'scheduling'
-- - Endpoints businessscenario MUST be 'Primary' or 'Copy'
-- - DELETE operations are NOT supported (logged as WARNING, ignored)
-- ============================================================================

-- ============================================================================
-- SECTION 1: CLEANUP (Run first to start fresh)
-- ============================================================================

-- Delete any existing test data from previous runs
DELETE FROM pathwaysdos.serviceendpoints WHERE serviceid = 99999;
DELETE FROM pathwaysdos.services WHERE id = 99999;

-- ============================================================================
-- SECTION 2: SETUP - CREATE COMPLETE TEST SERVICE
-- ============================================================================

-- Create a complete GP Practice service with all required fields
INSERT INTO pathwaysdos.services
(id, uid, name, publicname, odscode, address, town, postcode,
 publicphone, nonpublicphone, email, web, typeid, statusid,
 createddate, modifieddate, createdby, modifiedby)
VALUES
(99999, 'test-service-ftrs-1369', 'FTRS-1369 Test GP Practice', 'FTRS-1369 Test GP Practice',
 'A99999', -- Valid GP Practice ODS code format
 '123 Test Street', 'London', 'SW1A 1AA',
 '01234567890', '01234567891', 'test-ftrs-1369@nhs.uk', 'https://test.nhs.uk',
 100, -- typeid 100 = GP Practice
 1,   -- statusid 1 = Active
 NOW(), NOW(), 'test-user', 'test-user');

-- Verify service was created correctly
SELECT id, publicname, odscode, typeid, statusid, address, postcode, town
FROM pathwaysdos.services
WHERE id = 99999;

-- ============================================================================
-- SECTION 3: TEST SCENARIO 1 - INSERT ENDPOINT
-- ============================================================================
-- Test: Insert a new endpoint with VALID values
-- Expected Result: Migration should SUCCEED
-- Expected Lambda Logs:
--   - "Transformer GPPracticeTransformer selected for record"
--   - "Item put into DynamoDB table" (3 times: Organisation, Location, HealthcareService)
--   - "Record successfully migrated"
--   - "Data Migration ETL Pipeline completed successfully"
-- ============================================================================

-- STEP 1: Insert new endpoint with CORRECT values
INSERT INTO pathwaysdos.serviceendpoints
(id, serviceid, address, endpointorder, transport, format, interaction, businessscenario)
VALUES
(999991, 99999, 'https://test-ftrs-1369-insert.nhs.uk', 1,
 'http',              -- MUST be lowercase!
 'application/fhir',  -- Valid MIME type
 'scheduling',        -- Valid interaction
 'Primary');          -- Must be 'Primary' or 'Copy'

-- STEP 2: Verify insertion
SELECT id, serviceid, address, transport, format, interaction, businessscenario
FROM pathwaysdos.serviceendpoints
WHERE id = 999991;

-- STEP 3: Wait 10-30 seconds, then check CloudWatch logs
-- Expected: SUCCESS - migration completed, data in DynamoDB

-- ============================================================================
-- SECTION 4: TEST SCENARIO 2 - INSERT WITH INVALID VALUES (Negative Test)
-- ============================================================================
-- Test: Insert endpoint with INVALID values
-- Expected Result: Migration should FAIL with validation errors
-- Expected Lambda Logs:
--   - "Transformer GPPracticeTransformer selected for record"
--   - ERROR: "4 validation errors for Endpoint"
--   - connectionType: Input should be 'itk', 'email', 'telno' or 'http'
--   - payloadMimeType: Input should be valid MIME type
--   - description: Input should be 'Primary' or 'Copy'
--   - payloadType: Input should be valid URN or 'scheduling'
-- ============================================================================

-- STEP 1: Insert endpoint with WRONG values (intentionally)
INSERT INTO pathwaysdos.serviceendpoints
(id, serviceid, address, endpointorder, transport, format, interaction, businessscenario)
VALUES
(999992, 99999, 'https://test-ftrs-1369-invalid.nhs.uk', 2,
 'HTTP',              -- WRONG: uppercase (should be lowercase 'http')
 'JSON',              -- WRONG: not a valid MIME type
 'test',              -- WRONG: not a valid interaction
 'INVALID');          -- WRONG: should be 'Primary' or 'Copy'

-- STEP 2: Verify insertion (record created in DB)
SELECT id, serviceid, address, transport, format, interaction, businessscenario
FROM pathwaysdos.serviceendpoints
WHERE id = 999992;

-- STEP 3: Wait 10-30 seconds, then check CloudWatch logs
-- Expected: ERROR - 4 validation errors, migration failed

-- ============================================================================
-- SECTION 5: TEST SCENARIO 3 - UPDATE ENDPOINT
-- ============================================================================
-- Test: Update existing endpoint
-- Expected Result: Migration re-triggered, SUCCESS
-- Expected Lambda Logs:
--   - "Transformer GPPracticeTransformer selected for record"
--   - "Record successfully migrated"
--   - Updated data in DynamoDB
-- ============================================================================

-- STEP 1: Update the valid endpoint (999991)
UPDATE pathwaysdos.serviceendpoints
SET address = 'https://test-ftrs-1369-UPDATED.nhs.uk',
    interaction = 'urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0'
WHERE id = 999991;

-- STEP 2: Verify update
SELECT id, serviceid, address, interaction
FROM pathwaysdos.serviceendpoints
WHERE id = 999991;

-- STEP 3: Wait 10-30 seconds, then check CloudWatch logs
-- Expected: SUCCESS - migration completed with updated values

-- ============================================================================
-- SECTION 6: TEST SCENARIO 4 - FIX INVALID ENDPOINT
-- ============================================================================
-- Test: Update invalid endpoint (999992) with correct values
-- Expected Result: Migration should now SUCCEED
-- ============================================================================

-- STEP 1: Fix the invalid endpoint
UPDATE pathwaysdos.serviceendpoints
SET transport = 'http',
    format = 'application/fhir',
    interaction = 'scheduling',
    businessscenario = 'Copy'
WHERE id = 999992;

-- STEP 2: Verify update
SELECT id, serviceid, address, transport, format, interaction, businessscenario
FROM pathwaysdos.serviceendpoints
WHERE id = 999992;

-- STEP 3: Wait 10-30 seconds, then check CloudWatch logs
-- Expected: SUCCESS - migration now works after fixing values

-- ============================================================================
-- SECTION 7: TEST SCENARIO 5 - DELETE ENDPOINT (Negative Test)
-- ============================================================================
-- Test: Delete endpoint
-- Expected Result: DELETE operation is NOT SUPPORTED
-- Expected Lambda Logs:
--   - WARNING: "Unsupported event method: DELETE"
--   - "Data Migration ETL Pipeline completed successfully"
--   - No actual deletion in DynamoDB (ignored)
-- ============================================================================

-- STEP 1: Delete one test endpoint
DELETE FROM pathwaysdos.serviceendpoints
WHERE id = 999992;

-- STEP 2: Verify deletion from source DB
SELECT id, serviceid, address
FROM pathwaysdos.serviceendpoints
WHERE serviceid = 99999;
-- Should show only 999991 (999992 deleted)

-- STEP 3: Wait 10-30 seconds, then check CloudWatch logs
-- Expected: WARNING "Unsupported event method: DELETE" - operation ignored

-- ============================================================================
-- SECTION 8: TEST SCENARIO 6 - UPDATE SERVICE (triggers endpoint migration)
-- ============================================================================
-- Test: Update service itself (not endpoint)
-- Expected Result: All endpoints for this service should be re-migrated
-- ============================================================================

-- STEP 1: Update service
UPDATE pathwaysdos.services
SET publicname = 'FTRS-1369 Test GP Practice UPDATED'
WHERE id = 99999;

-- STEP 2: Wait 10-30 seconds, then check CloudWatch logs
-- Expected: Migration re-runs for all endpoints of service 99999

-- ============================================================================
-- SECTION 9: VERIFICATION QUERIES
-- ============================================================================

-- Check all endpoints for test service
SELECT id, serviceid, address, transport, format, interaction, businessscenario
FROM pathwaysdos.serviceendpoints
WHERE serviceid = 99999
ORDER BY id;

-- Check service details
SELECT id, publicname, odscode, typeid, statusid, address, postcode, town,
       publicphone, nonpublicphone, email
FROM pathwaysdos.services
WHERE id = 99999;

-- ============================================================================
-- SECTION 10: CLEANUP (Run after collecting all logs)
-- ============================================================================

-- Remove test endpoints
DELETE FROM pathwaysdos.serviceendpoints WHERE serviceid = 99999;

-- Remove test service
DELETE FROM pathwaysdos.services WHERE id = 99999;

-- Verify cleanup
SELECT COUNT(*) as remaining_test_data
FROM pathwaysdos.serviceendpoints
WHERE serviceid = 99999;

-- ============================================================================
-- SECTION 11: EXPECTED RESULTS SUMMARY
-- ============================================================================

/*
TEST SCENARIO RESULTS:

1. INSERT with valid values (999991):
   ✅ SUCCESS - Migration completed
   ✅ Data in DynamoDB (Organisation, Location, HealthcareService)

2. INSERT with invalid values (999992):
   ❌ FAILURE - 4 validation errors
   - connectionType: 'HTTP' not in ['itk', 'email', 'telno', 'http']
   - payloadMimeType: 'JSON' not valid
   - description: 'INVALID' not in ['Primary', 'Copy']
   - payloadType: 'test' not valid

3. UPDATE valid endpoint (999991):
   ✅ SUCCESS - Migration re-triggered with new values

4. FIX invalid endpoint (999992):
   ✅ SUCCESS - After fixing values, migration works

5. DELETE endpoint (999992):
   ⚠️  WARNING - DELETE not supported, operation ignored

6. UPDATE service (99999):
   ✅ SUCCESS - All service endpoints re-migrated

VALIDATION RULES CONFIRMED:
- transport: must be lowercase 'http', 'itk', 'email', or 'telno'
- format: must be valid MIME type (application/fhir, application/pdf, etc.)
- interaction: must be valid NHS ITK URN or 'scheduling'
- businessscenario: must be 'Primary' or 'Copy'
- Service must have: valid ODS code, statusid=1, complete address, contact details
*/

-- ============================================================================
-- END OF TEST SCRIPT
-- ============================================================================
