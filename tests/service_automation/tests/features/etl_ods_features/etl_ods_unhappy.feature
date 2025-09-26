@etl-ods @ftrs-pipeline
Feature: ETL Event Flow - Error Handling

  Scenario Outline: Verify error handling when invalid date parameter is sent to Lambda
    Given I invoke the lambda with invalid date "<invalid_date>"
    Then the lambda should return status code 400
    And the error message should be "Date must be in YYYY-MM-DD format"

    Examples:
      | invalid_date |
      | 2025-13-01   |
      | 01-01-2025   |
      | invalid-date |
      | ""           |

  Scenario: Lambda invoked without required parameters
    Given I invoke the lambda without required parameters
    Then the lambda should return status code 400
    And the error message should be "Date parameter is required"

  Scenario: Lambda invoked with a long past date
    Given I invoke the lambda with a long past date "2000-01-01"
    Then the lambda should return status code 400
    And the error message should be "Date must not be more than 185 days in the past"
