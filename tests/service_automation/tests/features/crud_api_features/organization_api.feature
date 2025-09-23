@crud-org-api @ftrs-pipeline
Feature: Organization API Endpoint


  Scenario: Retrieve Organization
    When I request data from the "crud" endpoint "Organization"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "10" "Organization" resources


  Scenario: Update organization for specific ODS Code
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I update the organization details for ODS Code
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "information"
    And the OperationOutcome contains an issue with code "success"
    And the OperationOutcome contains an issue with diagnostics "Organisation updated successfully"
    And the data in the database matches the inserted payload

  Scenario: Updating an organisation with identical data returns a successful response
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I update the organization details for ODS Code
    Then I receive a status code "200" in response and save the modifiedBy timestamp
    When I update the organisation details using the same data for the ODS Code
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "information"
    And the OperationOutcome contains an issue with code "information"
    And the OperationOutcome contains an issue with diagnostics "No changes made to the organisation"
    And the database matches the inserted payload with the same modifiedBy timestamp

  Scenario: Update Organisation with only mandatory fields
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I update the organization details for ODS Code with mandatory fields only
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "information"
    And the OperationOutcome contains an issue with code "success"
    And the OperationOutcome contains an issue with diagnostics "Organisation updated successfully"
    And the data in the database matches the inserted payload with telecom null

  Scenario Outline: Update Organisation with special characters for specific fields
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "<field>" field to "<value>"
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the database reflects "<field>" with value "<value>"

    Examples:
      | field   | value                           |
      | name    | MEDICAL PRACTICE - !COVID LOCAL |
      | type    | !SURGERY                        |
      | telecom | 9876543210(                     |



