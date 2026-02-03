@feature_flags @data_migration @integration

Feature: Feature Flags Integration with Lambda Functions

  Background:
    Given the test environment is configured
    And DynamoDB tables are ready


  Scenario: Queue populator Lambda reads feature flag from AppConfig
    Given AppConfig has feature flag "DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED" set to true
    And the queue populator Lambda is deployed with AppConfig integration
    When the queue populator Lambda handler is invoked
    Then the Lambda should successfully read the feature flag
    And the Lambda should log whether the feature is enabled or disabled
    And the Lambda execution should complete without errors


  Scenario: Processor Lambda initializes feature flags client successfully
    Given AppConfig has feature flag "DATA_MIGRATION_VALIDATION_ENABLED" set to true
    And the processor Lambda is deployed with AppConfig integration
    When the processor Lambda initializes FeatureFlagsClient
    Then the Lambda should successfully retrieve the AppConfig configuration
    And the feature flag value should be cached for 45 seconds


  Scenario: Lambda reads enabled feature flag from AppConfig
    Given AppConfig has feature flag "DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED" set to true
    When the queue populator Lambda reads the feature flag
    Then the feature flag should be evaluated as enabled
    And the flag evaluation should be logged in CloudWatch


  Scenario: Lambda reads disabled feature flag from AppConfig
    Given AppConfig has feature flag "DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED" set to false
    When the queue populator Lambda reads the feature flag
    Then the feature flag should be evaluated as disabled
    And the flag evaluation should be logged in CloudWatch


  Scenario Outline: Multiple Lambdas read different feature flags independently
    Given AppConfig has feature flag "<flag_name>" set to <flag_value>
    When the Lambda reads flag "<flag_name>"
    Then the flag should be evaluated as <expected_result>

    Examples:
      | flag_name                                  | flag_value | expected_result |
      | DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED | true       | enabled         |
      | DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED | false      | disabled        |
      | DATA_MIGRATION_VALIDATION_ENABLED         | true       | enabled         |
      | INCREMENTAL_UPDATE_FEATURE_ENABLED        | false      | disabled        |


  Scenario: Lambda logs feature flag evaluation details to CloudWatch
    Given AppConfig has feature flag "LOGGING_TEST_FLAG" set to true
    And logging is configured to DEBUG level
    When the Lambda reads flag "LOGGING_TEST_FLAG"
    Then the CloudWatch logs should contain flag name "LOGGING_TEST_FLAG"
    And the CloudWatch logs should contain evaluation result "true"
    And the CloudWatch logs should contain the flag source

