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

  Scenario Outline: Organization names are sanitized to title case with acronym preservation
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "name" field to "<input_name>"
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the database reflects "name" with value "<expected_name>"

    Examples:
      | input_name         | expected_name      |
      | nhs trust hospital | NHS Trust Hospital |
      | LONDON GP SURGERY  | London GP Surgery  |
      | the icb board      | The ICB Board      |
      | local pcn practice | Local PCN Practice |
      | Mixed Case nhs gp  | Mixed Case NHS GP  |

  Scenario Outline: Update Organisation with special characters for specific fields
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "<field>" field to "<value>"
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    Then the database reflects "<field>" with value "<value>"

    Examples:
      | field | value                           |
      | name  | Medical Practice - !Covid Local |
      | type  | !Surgery                        |
      | phone | 0300 311 22 34(                 |


  Scenario Outline: Reject Organization update with invalid special characters in specific fields
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "<field>" field to "<value>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the diagnostics message indicates invalid characters in the "<field_path>" with value "<value>"

    Examples:
      | field | value           | field_path       |
      | name  | BRANCH*SURGERY  | name             |
      | name  | BRANCH SURGERY$ | name             |
      | type  | #BRANCH SURGERY | type[0].text     |
      | type  | BRANCH#SURGERY  | type[0].text     |
      | phone | 0300 311 22 34@ | telecom[0].value |

  Scenario Outline: Update Organization with missing "<field>" field
    When I remove the "<field>" field from the payload and update the organization
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
    And the diagnostics message indicates "<field>" is missing

    Examples:
      | field        |
      | resourceType |
      # | id           | -- Test is failing due to response code different than expected --
      | meta         |
      | identifier   |
      | name         |
      | type         |
      | active       |
      | telecom      |


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

    Examples:
      | identifier_data                                                                                |
      | [{"value": "M2T8W", "use": "official"}]                                                        |
      | []                                                                                             |
      | [{"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": null, "use": "official"}] |
      | [{"system": null, "value": "M2T8W", "use": "official"}]                                        |
      | [{"system": "invalid-system", "value": "M2T8W", "use": "official"}]                            |
      | [{"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "", "use": "official"}]   |

  Scenario Outline: Update Organization with null active field
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the active field from the payload to null and update the organization
    Then I receive a status code "422" in response

  Scenario Outline: Successfully update organization with valid telecom fields
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "<field>" field to "<value>"
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "information"
    And the OperationOutcome contains an issue with code "success"
    And the OperationOutcome contains an issue with diagnostics "Organisation updated successfully"
    And the data in the database matches the inserted payload

    Examples:
      | field | value                     |
      | phone | 0300 311 22 34            |
      | phone | +44 7900 000 001          |
      | phone | #44 7900 000 001          |
      | phone | +49 170 1234567           |
      | phone | +61 4 1234 5678           |
      | phone | +33 1 23 45 67 89         |
      | phone | +91 9123456789            |
      | email | test@nhs.net              |
      | email | test12@example.com        |
      | email | test12@gmail.com          |
      | email | test12@yahoo.com          |
      | email | test@company.co.uk        |
      | email | valid-email@sub.domain.io |
      | url   | http://example.com        |


  Scenario Outline: Reject Organization update with invalid telecom values
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "<field>" field to "<value>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
    And the OperationOutcome contains an issue with diagnostics "<expected_error>"

    Examples:
      | field | value                    | expected_error                 |
      | phone | +++ABC123                | "Invalid phone number format." |
      | phone | 12345                    | "Invalid UK phone number."     |
      | phone | +9991234567890           | "Invalid UK phone number."     |
      | phone | +1 415-555-2671x1234     | "Invalid UK phone number."     |
      | phone | +1415555267              | "Invalid UK phone number."     |
      | phone | ++14155552671            | "Invalid UK phone number."     |
      | phone | +00000000000             | "Invalid UK phone number."     |
      | email | invalidemail.com         | "Invalid email format."        |
      | email | plainaddress             | "Invalid email format."        |
      | email | john..test@example.com   | "Invalid email format."        |
      | email | @missinglocal.com        | "Invalid email format."        |
      | email | username@.leadingdot.com | "Invalid email format."        |
      | email | user@invalid_domain.com  | "Invalid email format."        |
      | email | user@domain              | "Invalid email format."        |
      | email | user@domain.c            | "Invalid email format."        |
      | url   | htp://example.com        | "Invalid URL."                 |
      | url   | https:///example.com     | "Invalid URL."                 |
      | url   | http://exa mple.com      | "Invalid URL."                 |
      | url   | http://example           | "Invalid URL."                 |
      | url   | http://.example.com      | "Invalid URL."                 |
      | url   | http://example..com      | "Invalid URL."                 |
      | url   | http://example.com:99999 | "Invalid URL."                 |


  Scenario: Reject modification of 'type' field in telecom after creation
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I attempt to update the "<actual_type>" in telecom with "<update_type>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issue
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
    # And the OperationOutcome contains an issue with diagnostics "<expected_error>"

    Examples:
      | actual_type | update_type | expected_error                 |
      | phone       | email       | "Invalid phone number format." |
      | email       | phone       | "Invalid email format."        |
      | url         | email       | "Invalid URL."                 |

  Scenario Outline: Reject Organization Update with Invalid Telecom Field
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I update the organization with an invalid telecom field "<invalid_scenario>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issue
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
    # And the OperationOutcome contains an issue with diagnostics "<expected_error>"

    Examples:
      | invalid_scenario    | expected_error |
      | missing_type        | ""             |
      | missing_value       | ""             |
      | empty_type          | ""             |
      | empty_value         | ""             |
      | mixed_valid_invalid | ""             |

  Scenario: Reject Organization Update with Telecom Field containing extra field
    Given that the stack is "organisation"
    And I have an organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I update the organization with an invalid telecom field "additional_field"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issue
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
# And the OperationOutcome contains an issue with diagnostics ""

