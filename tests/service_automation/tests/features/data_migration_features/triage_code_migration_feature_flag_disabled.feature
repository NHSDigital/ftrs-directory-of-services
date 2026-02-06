@data-migration
Feature: SYSTEM - Triage Code Migration with Feature Flag Disabled

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Triage codes migration is skipped when DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED is disabled
    Given the feature flag 'DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED' is set to 'false'
    When triage code full migration is executed
    Then there are no records in table 'triage-code'
