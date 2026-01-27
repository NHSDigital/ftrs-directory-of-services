@etl-ods-mock @ftrs-pipeline
Feature: ETL ODS Mock - Upstream API Error Handling

  Background:
    Given the ETL ODS processor Lambda is configured with ODS mock

  Scenario: ETL ODS processes successful response from upstream API
    When I trigger the Lambda with happy path scenario
  # Then the Lambda should process the organizations successfully

  Scenario: ETL ODS handles empty results from upstream API
    When I trigger the Lambda with empty payload scenario
    Then the Lambda should handle empty results gracefully

  Scenario: ETL ODS handles invalid data types from upstream API
    When I trigger the Lambda with invalid data scenario
    Then the Lambda should handle the validation error


  Scenario: ETL ODS handles missing required fields from upstream API
    When I trigger the Lambda with missing required fields scenario
    Then the Lambda should handle missing fields gracefully

  Scenario: ETL ODS handles extra unexpected fields from upstream API
    When I trigger the Lambda with extra unexpected field scenario
    Then the Lambda should handle unexpected fields gracefully

  Scenario: ETL ODS handles request too old scenario from upstream API
    When I trigger the Lambda with request too old scenario
    Then the Lambda should handle old requests gracefully

  Scenario: ETL ODS handles unauthorized error from upstream API
    When I trigger the Lambda with unauthorized scenario
    Then the Lambda should handle the authorization error

  Scenario: ETL ODS handles server error from upstream API
    When I trigger the Lambda with server error scenario
    Then the Lambda should handle upstream server errors

  Scenario: ETL ODS handles unknown resource type from upstream API
    When I trigger the Lambda with unknown resource type scenario
    Then the Lambda should handle unknown resource types
