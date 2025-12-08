-- ============================================================================
-- MANUAL TEST SCRIPT FOR FTRS-1369: serviceendpoints trigger testing
-- ============================================================================
-- Author: Manual Testing
-- Date: 2025-12-08
-- Purpose: Test serviceendpoints table triggers that invoke Lambda functions
--
-- Prerequisites:
-- 1. Access to dev database where trigger is deployed
-- 2. Ability to monitor Lambda logs (CloudWatch)
-- 3. Ability to check SQS queue
-- ============================================================================

-- ============================================================================
-- SECTION 1: PRE-TEST VERIFICATION
-- ============================================================================

-- Check if trigger exists on serviceendpoints table
SELECT
    trigger_name,
    event_manipulation,
    action_statement,
    action_timing
FROM information_schema.triggers
WHERE event_object_table = 'serviceendpoints'
AND event_object_schema = 'pathwaysdos';

-- Check if the trigger function exists
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'pathwaysdos'
AND routine_name = 'related_service_change_notify';

-- ============================================================================
-- SECTION 2: IDENTIFY TEST DATA
-- ============================================================================

-- Find a GP Practice service for testing
SELECT s.id, s.name, s.uid, st.name as service_type
FROM pathwaysdos.services s
JOIN pathwaysdos.servicetypes st ON s.typeid = st.id
WHERE st.name = 'GP Practice'
LIMIT 5;

-- Example result: service_id = 45349 (Template - GP in Hours)

-- Check existing endpoints for this service
SELECT id, serviceid, address, endpointorder, transport, format
FROM pathwaysdos.serviceendpoints
WHERE serviceid = 45349;

-- ============================================================================
-- SECTION 3: TEST SCENARIO 1 - INSERT
-- ============================================================================
-- Expected Trigger Behavior:
-- - Lambda should be invoked with:
--   {
--     "table_name": "serviceendpoints",
--     "method": "INSERT",
--     "service_id": "45349",
--     "record_id": "<new_endpoint_id>"
--   }
-- - Processor lambda should sync the service (service_id: 45349)
-- ============================================================================

-- STEP 1: Insert new serviceendpoint
INSERT INTO pathwaysdos.serviceendpoints
(id, serviceid, address, endpointorder, transport, format, interaction, businessscenario)
VALUES
(385010, 45349, 'https://test-ftrs-1369-insert.nhs.uk', 99, 'HTTP', 'JSON', 'test', 'FTRS-1369-INSERT-TEST');

-- STEP 2: Get the inserted record ID
SELECT id, serviceid, address, businessscenario
FROM pathwaysdos.serviceendpoints
WHERE businessscenario = 'FTRS-1369-INSERT-TEST'
ORDER BY id DESC LIMIT 1;

-- Note down the ID: _____________

-- STEP 3: Verify Lambda invocation
-- ACTION: Check CloudWatch logs for queue_populator lambda
-- ACTION: Check SQS queue for message with table_name='serviceendpoints'
-- ACTION: Check service_migration lambda logs for service_id=45349

-- ============================================================================
-- SECTION 4: TEST SCENARIO 2 - UPDATE
-- ============================================================================
-- Expected Trigger Behavior:
-- - Lambda should be invoked with:
--   {
--     "table_name": "serviceendpoints",
--     "method": "UPDATE",
--     "service_id": "45349",
--     "record_id": "<endpoint_id>"
--   }
-- ============================================================================

-- STEP 1: Update the test endpoint
-- Replace <ENDPOINT_ID> with the ID from Section 3, Step 2
UPDATE pathwaysdos.serviceendpoints
SET address = 'https://test-ftrs-1369-updated.nhs.uk',
    businessscenario = 'FTRS-1369-UPDATE-TEST'
WHERE businessscenario = 'FTRS-1369-INSERT-TEST';

-- STEP 2: Verify the update
SELECT id, serviceid, address, businessscenario
FROM pathwaysdos.serviceendpoints
WHERE businessscenario = 'FTRS-1369-UPDATE-TEST';

-- STEP 3: Verify Lambda invocation
-- ACTION: Check CloudWatch logs for queue_populator lambda
-- ACTION: Confirm method='UPDATE' in the payload
-- ACTION: Check service_migration lambda processed the update

-- ============================================================================
-- SECTION 5: TEST SCENARIO 3 - DELETE
-- ============================================================================
-- Expected Trigger Behavior:
-- - Lambda should be invoked with:
--   {
--     "table_name": "serviceendpoints",
--     "method": "DELETE",
--     "service_id": "45349",
--     "record_id": "<endpoint_id>"
--   }
-- ============================================================================

-- STEP 1: Delete the test endpoint
DELETE FROM pathwaysdos.serviceendpoints
WHERE businessscenario = 'FTRS-1369-UPDATE-TEST';

-- STEP 2: Verify deletion
SELECT COUNT(*) as remaining_test_records
FROM pathwaysdos.serviceendpoints
WHERE businessscenario LIKE 'FTRS-1369%';
-- Should return 0

-- STEP 3: Verify Lambda invocation
-- ACTION: Check CloudWatch logs for queue_populator lambda
-- ACTION: Confirm method='DELETE' in the payload
-- ACTION: Check service_migration lambda processed the deletion

-- ============================================================================
-- SECTION 6: POST-TEST CLEANUP
-- ============================================================================

-- Clean up any remaining test records (safety net)
DELETE FROM pathwaysdos.serviceendpoints
WHERE businessscenario LIKE 'FTRS-1369%';

-- Verify cleanup
SELECT COUNT(*) FROM pathwaysdos.serviceendpoints
WHERE businessscenario LIKE 'FTRS-1369%';

-- ============================================================================
-- SECTION 7: MONITORING CHECKLIST
-- ============================================================================

/*
CHECKLIST FOR EACH TEST SCENARIO:

□ 1. SQL statement executed successfully
□ 2. CloudWatch Logs - queue_populator lambda invoked
  - Check for log entry with table_name='serviceendpoints'
  - Verify correct method (INSERT/UPDATE/DELETE)
  - Verify correct service_id and record_id

□ 3. SQS Queue - Message published
  - Check DMS event queue for new message
  - Verify message body matches expected format

□ 4. CloudWatch Logs - service_migration lambda invoked
  - Check for log entry processing the service_id
  - Verify sync_service() was called with correct parameters

□ 5. Target Database - Service migrated
  - Check if service was updated in target database
  - Verify endpoint data matches source

COMMON ISSUES TO WATCH FOR:
- Trigger not firing (no Lambda invocation)
- Incorrect payload format (missing fields)
- Lambda permission errors (check IAM roles)
- SQS delivery failures
- Service migration errors (check processor logs)
*/

-- ============================================================================
-- SECTION 8: ADDITIONAL VERIFICATION QUERIES
-- ============================================================================

-- Check if multiple endpoints are processed correctly (batch scenario)
SELECT serviceid, COUNT(*) as endpoint_count
FROM pathwaysdos.serviceendpoints
WHERE serviceid = 45349
GROUP BY serviceid;

-- Check service details for context
SELECT id, name, uid, publicname, statusid
FROM pathwaysdos.services
WHERE id = 45349;

-- ============================================================================
-- END OF TEST SCRIPT
-- ============================================================================
