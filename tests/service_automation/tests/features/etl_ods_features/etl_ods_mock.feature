@etl-ods-mock @ftrs-pipeline
Feature: ETL ODS Mock - Upstream API Error Handling

  Background:
    Given the ETL ODS processor Lambda is configured with ODS mock

  Scenario: ETL ODS processes successful response from upstream API
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-for-mock-session-seeded-repo.json"
    When I trigger the Lambda with happy path scenario
    Then the Lambda should process the organizations successfully
    And the message should be sent to the queue successfully
    And the Consumer should log the successful processing of the request
    And the CRUD API should log the update request for the organisation
    And the organisation data should be updated in DynamoDB

  Scenario: ETL ODS handles empty results from upstream API
    When I trigger the Lambda with empty payload scenario
    Then the Lambda should handle empty results gracefully

  Scenario: ETL ODS handles invalid data types from upstream API
    When I trigger the Lambda with invalid data scenario
    Then the Lambda should handle the validation error

  Scenario: ETL ODS handles missing required fields from upstream API
    When I trigger the Lambda with missing required fields scenario
    Then the Lambda should handle missing fields gracefully

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

  Scenario: ETL ODS handles invalid ODS format from upstream API
    When I trigger the Lambda with an invalid ODS format
    Then the Lambda should handle the invalid ODS format gracefully

  Scenario: ETL ODS handles extra unexpected fields from upstream API
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-for-mock-session-seeded-repo.json"
    When I trigger the Lambda with extra unexpected field scenario
    Then the Lambda should handle unexpected fields gracefully
    And the message should be sent to the queue successfully
    And the Consumer should log the successful processing of the request
    And the CRUD API should log the update request for the organisation
    And the extra unexpected fields should not be saved to DynamoDB

  Scenario: ETL ODS handles missing optional fields from upstream API
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-for-mock-session-seeded-repo.json"
    When I trigger the Lambda with missing optional fields scenario
    Then the Lambda should handle missing optional fields gracefully
    And the message should be sent to the queue successfully
    And the Consumer should log the successful processing of the request
    And the CRUD API should log the update request for the organisation
    And the telecom data should remain unchanged in DynamoDB

