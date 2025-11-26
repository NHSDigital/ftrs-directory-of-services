@etl-ods-mock @ftrs-pipeline
Feature: ETL ODS Mock - Upstream API Error Handling

  Background:
    Given the ETL ODS processor Lambda is configured with VTL mock

  Scenario: ETL ODS handles invalid data types from upstream API
    When I trigger the Lambda with invalid data scenario
    Then the Lambda should handle the validation error

  Scenario: ETL ODS handles unauthorized error from upstream API
    When I trigger the Lambda with unauthorized scenario
    Then the Lambda should handle the authorization error
