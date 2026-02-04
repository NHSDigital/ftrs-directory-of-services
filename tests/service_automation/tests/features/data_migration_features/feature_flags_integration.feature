@feature_flags @data_migration @integration

Feature: Feature Flags Integration with Lambda Functions

  Background:
    Given the test environment is configured
    And DynamoDB tables are ready


  Scenario: Queue populator Lambda handler reads enabled feature flag from AppConfig
    Given AppConfig returns "DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED" as enabled
    When the queue populator Lambda handler is invoked with an empty event
    Then the Lambda handler should execute successfully
    And the Lambda logs should contain "Healthcare service feature flag is enabled"


  Scenario: Queue populator Lambda handler reads disabled feature flag from AppConfig
    Given AppConfig returns "DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED" as disabled
    When the queue populator Lambda handler is invoked with an empty event
    Then the Lambda handler should execute successfully
    And the Lambda logs should contain "Healthcare service feature flag is disabled"


  Scenario: Lambda handler evaluates feature flags consistently across multiple invocations
    Given AppConfig returns "DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED" as enabled
    When the queue populator Lambda handler is invoked with an empty event
    Then the Lambda handler should execute successfully
    And the Lambda logs should contain "Healthcare service feature flag is enabled"
    When the queue populator Lambda handler is invoked again within 45 seconds
    Then the Lambda handler should execute successfully
    And the Lambda logs should contain "Healthcare service feature flag is enabled"

