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

  Scenario Outline: Reject Organization update with invalid special characters in specific fields
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "<field>" field to "<value>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the diagnostics message indicates invalid characters in the "<field_path>" with value "<value>"

    Examples:
      | field | value           | field_path   |
      | name  | BRANCH*SURGERY  | name         |
      | name  | BRANCH SURGERY$ | name         |
      | type  | #BRANCH SURGERY | type[0].text |
      | type  | BRANCH#SURGERY  | type[0].text |


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

  Scenario Outline: Reject Organization update with invalid identifier
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

  Scenario Outline: Reject Organization update with invalid value in active field
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "<field>" field to "<value>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"

    Examples:
      | field  | value  |
      | active | ""     |
      | active | null   |
      | active | "null" |


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
      | field | value               |
      | phone | 0300 311 22 34      |
      | phone | +44 7900 000 001    |
      | phone | 07900 000 001       |
      | phone | +44 (0) 7900 000001 |
      | email | test@nhs.net        |
      | email | test12@gmail.com    |
      | email | test12@yahoo.com    |
      | email | test@company.co.uk  |
      | url   | http://example.com  |
      | url   | https://example.com |

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
      | field | value                    | expected_error                                                                                                                 |
      | phone | +++ABC123                | Validation failed for the following resources: Telecom value field contains an invalid phone number: +++ABC123                 |
      | phone | 12345                    | Validation failed for the following resources: Telecom value field contains an invalid phone number: 12345                     |
      | phone | +9991234567890           | Validation failed for the following resources: Telecom value field contains an invalid phone number: +9991234567890            |
      | phone | +44 (0) 7911 123456      | Validation failed for the following resources: Telecom value field contains an invalid phone number: +44 (0) 7911 123456       |
      | phone | +1 415-555-2671x1234     | Validation failed for the following resources: Telecom value field contains an invalid phone number: +1 415-555-2671x1234      |
      | phone | +1415555267              | Validation failed for the following resources: Telecom value field contains an invalid phone number: +1415555267               |
      | phone | ++14155552671            | Validation failed for the following resources: Telecom value field contains an invalid phone number: ++14155552671             |
      | phone | +00000000000             | Validation failed for the following resources: Telecom value field contains an invalid phone number: +00000000000              |
      | phone | 0300 311 22 34@          | Validation failed for the following resources: Telecom value field contains an invalid phone number: 0300 311 22 34@           |
      | phone | #0300 311 22 34          | Validation failed for the following resources: Telecom value field contains an invalid phone number: #0300 311 22 34           |
      | phone | 0300-311-22-34           | Validation failed for the following resources: Telecom value field contains an invalid phone number: 0300-311-22-34            |
      | phone | <020 7972 3272           | Validation failed for the following resources: Telecom value field contains an invalid phone number: <020 7972 3272            |
      | phone | 020;7972;3272            | Validation failed for the following resources: Telecom value field contains an invalid phone number: 020;7972;3272             |
      | phone | 07900#000001             | Validation failed for the following resources: Telecom value field contains an invalid phone number: 07900#000001              |
      | phone | +44/7911/123456          | Validation failed for the following resources: Telecom value field contains an invalid phone number: +44/7911/123456           |
      | phone | 0300,311,22,34           | Validation failed for the following resources: Telecom value field contains an invalid phone number: 0300,311,22,34            |
      | phone | 0300_311_22_34           | Validation failed for the following resources: Telecom value field contains an invalid phone number: 0300_311_22_34            |
      | phone | +44~7911^123456          | Validation failed for the following resources: Telecom value field contains an invalid phone number: +44~7911^123456           |
      | phone | +49 170 1234567          | Validation failed for the following resources: Telecom value field contains an invalid phone number: +49 170 1234567           |
      | phone | +61 4 1234 5678          | Validation failed for the following resources: Telecom value field contains an invalid phone number: +61 4 1234 5678           |
      | phone | +33 1 23 45 67 89        | Validation failed for the following resources: Telecom value field contains an invalid phone number: +33 1 23 45 67 89         |
      | phone | +91 9123456789           | Validation failed for the following resources: Telecom value field contains an invalid phone number: +91 9123456789            |
      | email | invalidemail.com         | Validation failed for the following resources: Telecom value field contains an invalid email address: invalidemail.com         |
      | email | plainaddress             | Validation failed for the following resources: Telecom value field contains an invalid email address: plainaddress             |
      | email | john..test@example.com   | Validation failed for the following resources: Telecom value field contains an invalid email address: john..test@example.com   |
      | email | @missinglocal.com        | Validation failed for the following resources: Telecom value field contains an invalid email address: @missinglocal.com        |
      | email | username@.leadingdot.com | Validation failed for the following resources: Telecom value field contains an invalid email address: username@.leadingdot.com |
      | email | user@invalid_domain.com  | Validation failed for the following resources: Telecom value field contains an invalid email address: user@invalid_domain.com  |
      | email | user@domain              | Validation failed for the following resources: Telecom value field contains an invalid email address: user@domain              |
      | email | user@domain.c            | Validation failed for the following resources: Telecom value field contains an invalid email address: user@domain.c            |
      | url   | htp://example.com        | Validation failed for the following resources: Telecom value field contains an invalid url: htp://example.com                  |
      | url   | http://exa mple.com      | Validation failed for the following resources: Telecom value field contains an invalid url: http://exa mple.com                |
      | url   | http://example.com:99999 | Validation failed for the following resources: Telecom value field contains an invalid url: http://example.com:99999           |

  Scenario: Reject modification of 'type' field in telecom after creation
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I attempt to update the "<actual_type>" in telecom with "<update_type>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
    And the OperationOutcome contains an issue with diagnostics "<expected_error>"

    Examples:
      | actual_type | update_type | expected_error                                                                                                               |
      | phone       | email       | Validation failed for the following resources: Telecom value field contains an invalid email address: 0300 311 22 34         |
      | email       | phone       | Validation failed for the following resources: Telecom value field contains an invalid phone number: test678@nhs.net         |
      | url         | email       | Validation failed for the following resources: Telecom value field contains an invalid email address: https://example123.com |

  Scenario Outline: Reject Organization Update with Invalid Telecom Field
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I update the organization with an invalid telecom field "<invalid_scenario>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"

    Examples:
      | invalid_scenario    |
      | missing_type        |
      | missing_value       |
      | empty_type          |
      | empty_value         |
      | mixed_valid_invalid |
      | unsupported_system  |

  Scenario: Reject Organization Update with Telecom Field containing extra field
    When I update the organization with an invalid telecom field "additional_field"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
    And the diagnostics message indicates unexpected field "extra_field" with value "unexpected"

  Scenario Outline: Update Organization with legal dates
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I update the organization with legal dates start "<legal_start>" and end "<legal_end>"
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the database reflects "legalStartDate" with value "<expected_db_start>"
    And the database reflects "legalEndDate" with value "<expected_db_end>"

    Examples:
      | legal_start | legal_end  | expected_db_start | expected_db_end |
      | 2020-01-15  | 2025-12-31 | 2020-01-15        | 2025-12-31      |
      | 2020-02-15  | null       | 2020-02-15        | None            |
      | 2020-01-15  | 2024-12-31 | 2020-01-15        | 2024-12-31      |
      | 2020-02-29  | 2028-02-29 | 2020-02-29        | 2028-02-29      |

  Scenario Outline: Reject Organization update with invalid extensions for legal date
    Given that the stack is "organisation"
    When I update the organization with an invalid TypedPeriod extension "<invalid_scenario>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"
    And I receive the diagnostics "<expected_error>"

    Examples:
      | invalid_scenario                  | expected_error                                                                                                    |
      | missing dateType                  | TypedPeriod extension must contain dateType and period                                                            |
      | missing period                    | TypedPeriod extension must contain dateType and period                                                            |
      | non-Legal dateType                | dateType must be Legal                                                                                            |
      | invalid periodType extension url  | Invalid extension URL: https://fhir.nhs.uk/England/StructureDefinition/Extension-England-InvalidTypedPeriod       |
      | invalid periodType system         | dateType system must be 'https://fhir.nhs.uk/England/CodeSystem/England-PeriodType'                               |
      | invalid role extension url        | Invalid extension URL: https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole-INVALID |
      | missing role extension url        | Extension URL must be present and cannot be empty or None                                                         |
      | empty role extension url          | Extension URL must be present and cannot be empty or None                                                         |
      | missing TypedPeriod extension url | OrganisationRole extension must contain at least one TypedPeriod extension                                        |
      | empty TypedPeriod extension url   | OrganisationRole extension must contain at least one TypedPeriod extension                                        |
      | missing start date with end       | Legal period start date is required when TypedPeriod extension is present                                         |
      | missing both start and end        | Legal period start date is required when TypedPeriod extension is present                                         |

  Scenario Outline: Reject Organization update with invalid date format
    Given that the stack is "organisation"
    When I update the organization with invalid date format "<date_field>" value "<invalid_date>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"

    Examples:
      | date_field | invalid_date |
      | start      | 2020-13-45   |
      | start      | 20-01-2020   |
      | start      | 2020/01/15   |
      | start      | 2020-1-5     |
      | start      | 15-01-2020   |
      | start      | invalid      |
      | end        | 2025-13-45   |
      | end        | 25-12-2025   |
      | end        | 2025/12/31   |
      | end        | 2025-12-1    |

  Scenario Outline: Reject Organization update when start date matches end date
    Given that the stack is "organisation"
    When I update the organization with legal dates start "2025-01-01" and end "2025-01-01"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"


  Scenario Outline: Update Organization update with valid ods-code format
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "identifier" field to "<value>"
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "information"
    And the OperationOutcome contains an issue with code "success"
    And the OperationOutcome contains an issue with diagnostics "Organisation updated successfully"
    And the data in the database matches the inserted payload

    Examples:
      | value        |
      | 1            |
      | Z9           |
      | B76          |
      | A123         |
      | ABC123       |
      | abcDEF       |
      | abcDEF456    |
      | XyZ789       |
      | A1B2C3D4E5F6 |
      | ABCDEFGHIJKL |
      | 1234567890   |
      | TEST123456   |
      | CODE2025     |
      | M2T8W        |
      | 01234        |


  Scenario Outline: Reject Organization update with invalid ods-code format
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I set the "identifier" field to "<value>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "invalid"

    Examples:
      | value         |
      | ""            |
      | 1234567890123 |
      | TOOLONG123456 |
      | !ABC123       |
      | ABC123!       |
      | @#$%^&*       |
      | ABC_123       |
      | abc.def       |
      | ABC 123       |
      | ABC-123       |
      | 123_456       |


  Scenario: Successfully update organization with empty telecom list
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I update the organization with an invalid telecom field "empty_telecom"
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "information"
    And the OperationOutcome contains an issue with code "success"
    And the OperationOutcome contains an issue with diagnostics "Organisation updated successfully"
    And the data in the database matches the inserted payload

