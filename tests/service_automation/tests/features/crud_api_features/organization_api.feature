@crud-org-api @ftrs-pipeline
Feature: Organization API Endpoint

  Scenario: Retrieve Organization
    When I request data from the "crud" endpoint "Organization"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "10" "Organization" resources

  Scenario: Update Organization for specific ODS Code
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

  Scenario: Updating an Organisation with identical data returns a successful response
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

  Scenario Outline: Organization names are sanitized to title case with acronym preservation
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "name" field to "<input_name>"
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the database reflects "name" with value "<expected_name>"

    Examples:
      | input_name              | expected_name           |
      | nhs trust hospital      | NHS Trust Hospital      |
      | LONDON GP SURGERY       | London GP Surgery       |
      | the icb board           | The ICB Board           |
      | local pcn practice      | Local PCN Practice      |
      | Mixed Case nhs gp       | Mixed Case NHS GP       |

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

  Scenario Outline: Reject Organization update with invalid special characters in specific fields
    When I set the "<field>" field to "<value>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
    And the diagnostics message indicates invalid characters in the "<field_path>" with value "<invalid_value>"

    Examples:
      | field   | value           | field_path       | invalid_value   |
      | name    | BRANCH*SURGERY  | name             | BRANCH*SURGERY  |
      | name    | BRANCH SURGERY$ | name             | BRANCH SURGERY$ |
      | type    | #BRANCH SURGERY | type[0].text     | #BRANCH SURGERY |
      | type    | BRANCH#SURGERY  | type[0].text     | BRANCH#SURGERY  |
      | telecom | 0123456@789     | telecom[0].value | 0123456@789     |

  Scenario Outline: Update Organization with missing "<field>" field
    When I remove the "<field>" field from the payload and update the organization
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

  Scenario: Update Organization with non-existent ID
    When I update the organization with a non-existent ID
    Then I receive a status code "404" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "not-found"
    And the OperationOutcome contains an issue with diagnostics "Organisation not found."

  Scenario: Update Organization with unexpected field in payload
    When I add an extra field "newfield" with value "foobar" to the payload and update the organization
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
    And the diagnostics message indicates unexpected field "newfield" with value "foobar"

  Scenario: Reject request with invalid Content-Type
    When I send a PUT request with invalid Content-Type to the organization API
    Then I receive a status code "415" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "unsupported-media-type"
    And the OperationOutcome contains an issue with diagnostics "PUT requests must have Content-Type 'application/fhir+json'"


  Scenario Outline: Update organization with valid identifier
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    And I have a valid organization payload with identifier "<identifier_data>"
    When I update the organization details with the identifier
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "information"
    And the OperationOutcome contains an issue with code "success"
    And the OperationOutcome contains an issue with diagnostics "Organisation updated successfully"
    And the data in the database matches the inserted payload

    Examples:
      | identifier_data                                                                             |
      | [{"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "M2T8W"}]              |
      | [{"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "M2T8W", "use": null}] |

  Scenario Outline: Update organization with invalid identifier
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    And I have a valid organization payload with identifier "<identifier_data>"
    When I update the organization details with the identifier
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"


    Examples:
      | identifier_data                                                                                |
      | [{"value": "M2T8W", "use": "official"}]                                                        |
      | []                                                                                             |
      | [{"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": null, "use": "official"}] |
      | [{"system": null, "value": "M2T8W", "use": "official"}]                                        |
      | [{"system": "invalid-system", "value": "M2T8W", "use": "official"}]                            |
      | [{"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "", "use": "official"}]   |



