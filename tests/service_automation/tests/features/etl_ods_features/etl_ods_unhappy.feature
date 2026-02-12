@etl-ods @data-sourcing
Feature: ETL Event Flow - Error Handling

  Background:
    Given the ETL ODS infrastructure is available

  # ==================== Extractor Validation Errors ====================
  Scenario Outline: Verify error handling when invalid date parameter is sent to ETL processor lambda
    Given I trigger the ODS ETL pipeline with invalid date "<invalid_date>"
    Then the lambda should return status code 400
    And the error message should be "Date must be in YYYY-MM-DD format"
    Then the Lambda should log the validation error "ETL_EXTRACTOR_029"

    Examples:
      | invalid_date |
      | 2025-13-01   |
      | 01-01-2025   |
      | invalid-date |
      | ""           |

  Scenario: ETL processor lambda invoked without required date parameter
    Given I trigger the ODS ETL pipeline without required parameters
    Then the lambda should return status code 400
    And the error message should be "Date parameter is required"
    Then the Lambda should log the validation error "ETL_EXTRACTOR_029"


  Scenario: ETL processor lambda invoked with a long past date
    Given I trigger the ODS ETL pipeline with a long past date "2000-01-01"
    Then the lambda should return status code 400
    And the error message should be "Date must not be more than 185 days in the past"
    Then the Lambda should log the validation error "ETL_EXTRACTOR_029"


  # ==================== Permanent Failures - Consumed Immediately ====================
  Scenario: Transform message with 404 error is consumed without retry
    Given I have a transform message that will fail with 404
    When the "transform" lambda processes the message
    Then the logs for the message should contain "Organisation not found in database for ods code"
    And the logs for the message should contain "Permanent failure"
    And the logs for the message should contain "consumed immediately"
    And the "transform" queue should not have message
    And the "transform" DLQ should not have message

  # ==================== Transform Permanent Errors - Consumed Immediately ====================
  Scenario: Transform message with malformed JSON is consumed immediately
    Given I have a transform message with malformed JSON
    When the "transform" lambda processes the message
    Then the logs for the message should contain "Error decoding json"
    And the logs for the message should contain "Permanent failure (status 400)"
    And the logs for the message should contain "consumed immediately"
    And the "transform" queue should not have message
    And the "transform" DLQ should not have message

  Scenario: Transform message with missing required fields is consumed immediately  
    Given I have a transform message with missing required fields
    When the "transform" lambda processes the message
    Then the logs for the message should contain "is missing required fields"
    And the logs for the message should contain "Permanent failure (status 400)"
    And the logs for the message should contain "consumed immediately"
    And the "transform" queue should not have message
    And the "transform" DLQ should not have message

  # ==================== Consumer Permanent Errors - Consumed Immediately ====================
  Scenario: Consumer message with 422 error is consumed immediately
    Given I have a consumer message that will fail with 422
    When the "load" lambda processes the message
    Then the logs for the message should contain "Permanent failure"
    And the logs for the message should contain "consumed immediately"
    And the logs for the message should contain "failed for message id"
    And the "load" queue should not have message
    And the "load" DLQ should not have message

  Scenario: Consumer message with malformed JSON is consumed immediately
    Given I have a consumer message with malformed JSON
    When the "load" lambda processes the message
    Then the logs for the message should contain "Error decoding json"
    And the logs for the message should contain "Permanent failure (status 400)"
    And the logs for the message should contain "consumed immediately"
    And the "load" queue should not have message
    And the "load" DLQ should not have message

  # ==================== Business Logic Validation ====================
  Scenario: Transformer handles invalid ODS code format
    Given I have a transform message with invalid ODS code format
    When the "transform" lambda processes the message
    Then the logs for the message should contain "ODS code validation failed"
    And the logs for the message should contain "Invalid ODS code"
    Then the logs for the message should contain "Permanent failure"
    And the logs for the message should contain "consumed immediately"

  Scenario: Transformer handles organisation with no identifier
    Given I have a transform message with organisation missing identifier
    When the "transform" lambda processes the message
    Then the logs for the message should contain "No ODS code identifier"
    Then the logs for the message should contain "Permanent failure (status 400)"
    And the logs for the message should contain "consumed immediately"
    And the "transform" queue should not have message
    And the "transform" DLQ should not have message
