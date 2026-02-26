@is-apim @integrated-search @dos-search-ods-code-api
@nhsd_apim_authorization(access="application",level="level3")
Feature: dos-search tests against the apim proxy

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"


  Scenario: I send a request to the dos-search organization endpoint by ODS Code via APIM with valid query parameters
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources
    And the response is valid against the dos-search schema for endpoint "/Organization"


  Scenario Outline: I send a request to the dos-search organization endpoint via APIM with invalid ODS code
    When I request data from the APIM endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Invalid identifier value: ODS code '<ods_code>' must follow format ^[A-Za-z0-9]{5,12}$"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
      | params                                                                                                   | ods_code      |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|&_revinclude=Endpoint:organization              |               |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|0123&_revinclude=Endpoint:organization          | 0123          |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|0123456789ABC&_revinclude=Endpoint:organization | 0123456789ABC |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|123@@@&_revinclude=Endpoint:organization        | 123@@@        |


  Scenario Outline: I send a request to the dos-search organization endpoint via APIM with invalid _revinclude value
    When I request data from the APIM endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "The request is missing the '_revinclude=Endpoint:organization' parameter, which is required to include linked Endpoint resources."
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
      | params                                                                      |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|M00081046&_revinclude=                      |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|M00081046&_revinclude=Invalid:value         |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|M00081046&_revinclude=ENDPOINT:ORGANIZATION |


  Scenario Outline: I send a request to the dos-search organization endpoint via APIM with invalid identifier system
    When I request data from the APIM endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "code-invalid"
    And the OperationOutcome contains an issue with diagnostics "Invalid identifier system '<identifier_system>' - expected 'https://fhir.nhs.uk/Id/ods-organization-code'"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
      | params                                                                             | identifier_system          |
      | identifier=\|M00081046&_revinclude=Endpoint:organization                           |                            |
      | identifier=invalidSystem\|M00081046&_revinclude=Endpoint:organization              | invalidSystem              |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-codeInvalid\|M00081046&_revinclude=Endpoint:organization | https://fhir.nhs.uk/Id/ods-organization-codeInvalid |


  Scenario Outline: I send a request to the dos-search organization endpoint via APIM with missing parameters
    When I request data from the APIM endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "required"
    And the OperationOutcome contains an issue with diagnostics "Missing required query parameter(s): <missing_param>"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
    | params                                                             | missing_param               |
    | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|M00081046 | '_revinclude'               |
    | _revinclude=Endpoint:organization                                  | 'identifier'                |
    |                                                                    | 'identifier', '_revinclude' |


Scenario Outline: I send a request to the dos-search organization endpoint by ODS Code via APIM with unexpected query parameter
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046&<unexpected_param>=<unexpected_value>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Unexpected query parameter(s): <unexpected_param>. Only 'identifier' and '_revinclude' are allowed."
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
      | unexpected_param | unexpected_value |
      | foo              | bar              |
      | _sort            | name             |


  Scenario Outline: I send a request to the dos-search organization endpoint by ODS Code via APIM with ODS code at valid boundary length
    When I request data from the APIM endpoint "Organization" with query params "identifier=https://fhir.nhs.uk/Id/ods-organization-code|<ods_code>&_revinclude=Endpoint:organization"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "0" "Organization" resources
    And the bundle contains "0" "Endpoint" resources
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
      | ods_code     |
      | ABCDE        |
      | ABCDE1234567 |
