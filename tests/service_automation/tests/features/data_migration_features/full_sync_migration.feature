@data-migration
Feature: Run Full Sync Service Migration
  As a test author
  I want to execute a full data migration for all services
  So that I can validate the migration process handles large-scale synchronization accurately and reports correct metrics

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Full sync migration with existing services
    When a full service migration is run
    Then the metrics should be 124256 total, 6569 supported, 117687 unsupported, 6418 transformed, 6418 migrated, 150 skipped and 1 errors
