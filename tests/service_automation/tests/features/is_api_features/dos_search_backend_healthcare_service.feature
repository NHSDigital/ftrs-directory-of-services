@is-api @integrated-search @dos-search-healthcare-service-api
Feature: API DoS Healthcare Service Search Backend

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And the dns for "dos-search" is resolvable
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    And I have a healthcare_service repo
    And I create a healthcare service model in the repo from json file "HealthcareService/healthcare-service-with-no-endpoints.json"

  Scenario: I search for HealthcareService by ODS Code with valid query parameters
    When I request data from the "dos-search" endpoint "HealthcareService" with query params "organization.identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "HealthcareService" resources

  Scenario: I search for HealthcareService by ODS Code with no matching organisation
    When I request data from the "dos-search" endpoint "HealthcareService" with query params "organization.identifier=https://fhir.nhs.uk/Id/ods-organization-code|NOTFOUND1"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "0" "HealthcareService" resources

  Scenario Outline: I search for HealthcareService with invalid ODS code
    When I request data from the "dos-search" endpoint "HealthcareService" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Invalid identifier value: ODS code '<ods_code>' must follow format ^[A-Za-z0-9]{5,12}$"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | params                                                                              | ods_code      |
      | organization.identifier=https://fhir.nhs.uk/Id/ods-organization-code\|              |               |
      | organization.identifier=https://fhir.nhs.uk/Id/ods-organization-code\|0123          | 0123          |
      | organization.identifier=https://fhir.nhs.uk/Id/ods-organization-code\|0123456789ABC | 0123456789ABC |
      | organization.identifier=https://fhir.nhs.uk/Id/ods-organization-code\|123@@@        | 123@@@        |

  Scenario Outline: I search for HealthcareService with invalid identifier system
    When I request data from the "dos-search" endpoint "HealthcareService" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "code-invalid"
    And the OperationOutcome contains an issue with diagnostics "Invalid identifier system '<identifier_system>' - expected 'https://fhir.nhs.uk/Id/ods-organization-code'"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | params                                                 | identifier_system   |
      | organization.identifier=\|M00081046                    |                     |
      | organization.identifier=invalidSystem\|M00081046       | invalidSystem       |
      | organization.identifier=odsOrganisationCode\|M00081046 | odsOrganisationCode |

  Scenario: I search for HealthcareService with missing identifier parameter
    When I request data from the "dos-search" endpoint "HealthcareService" with query params ""
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "required"
    And the OperationOutcome contains an issue with diagnostics "Missing required query parameter 'organization.identifier'"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding

  Scenario Outline: I search for HealthcareService with unexpected query parameter
    When I request data from the "dos-search" endpoint "HealthcareService" with query params "organization.identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046&<unexpected_param>=<unexpected_value>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Unexpected query parameter(s): <unexpected_param>. Only 'organization.identifier' is allowed."
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | unexpected_param | unexpected_value      |
      | foo              | bar                   |
      | junk             | 123                   |
