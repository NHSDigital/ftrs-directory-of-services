@apim-test
Feature: Organization API Endpoint via APIM

  Background: Set stack and seed repo
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"

  Scenario:Update Organization for specific ODS Code via APIM
    When I update the organization details for ODS Code via APIM
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "information"
    And the OperationOutcome contains an issue with code "success"
    And the OperationOutcome contains an issue with diagnostics "Organisation updated successfully"
    And the data in the database matches the inserted payload

  Scenario Outline: Update Organization with missing "<field>" field
    When I remove the "<field>" field from the payload and update the organization via APIM
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
    And the diagnostics message indicates "<field>" is missing

    Examples:
      | field  |
      | name   |
      | type   |
      | active |


