@etl-ods @ftrs-pipeline
Feature: ETL Event Flow - Error Handling

  Scenario Outline: Verify error handling when invalid date parameter is sent to ETL processor lambda
    Given I invoke the lambda with invalid date "<invalid_date>"
    Then the lambda should return status code 400
    And the error message should be "Date must be in YYYY-MM-DD format"

    Examples:
      | invalid_date |
      | 2025-13-01   |
      | 01-01-2025   |
      | invalid-date |
      | ""           |

  Scenario: ETL processor lambda invoked without required date parameter
    Given I invoke the lambda without required parameters
    Then the lambda should return status code 400
    And the error message should be "Date parameter is required"

  Scenario: ETL processor lambda invoked with a long past date
    Given I invoke the lambda with a long past date "2000-01-01"
    Then the lambda should return status code 400
    And the error message should be "Date must not be more than 185 days in the past"
