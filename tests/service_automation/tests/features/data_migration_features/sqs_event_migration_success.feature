@data-migration
Feature: SQS Event-Driven Migration - Service Insert Event
  As a test author
  I want to execute a data migration triggered by an SQS event
  So that I can verify the migration process correctly handles service insert events and updates the target system without errors

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Process SQS event for service INSERT
    When the data migration process is run for table 'services', ID '26579' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
