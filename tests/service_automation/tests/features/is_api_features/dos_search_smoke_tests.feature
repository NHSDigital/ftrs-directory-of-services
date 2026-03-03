@is-smoke
Feature: dos-search smoke tests
# These tests are intended to be run in INT/REF/PROD environments against deployed dos-search instances, and should not rely on specific test data being present.
# They are designed to smoke test basic functionality of the dos-search API, and should not be testing edge cases or error conditions that require specific data to be present.
Background: Set stack and select ODS code for testing from the organisation dynamo table
    Given that the stack is "dos-search"
    Given there is an Organisation with an ODS code in the repo



  Scenario: I search for Organization endpoint data by ODS Code via APIM with an existing ODS code from the Organisation dynamo table - smoke test
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the response is valid against the dos-search schema for endpoint "/Organization"


  Scenario: I search for Organization endpoint data by ODS Code via APIM with an ODS code that does not exist in the Organisation dynamo table - smoke test
    When I request data from the APIM endpoint "Organization" with an odscode that does not exist in the organisation dynamo table
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "0" "Organization" resources
    And the response is valid against the dos-search schema for endpoint "/Organization"


  Scenario Outline: I search for Organization endpoint data by ODS Code via APIM with invalid ODS code - smoke test
    When I request data from the smoke test APIM endpoint "Organization" with query params "<params>"
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


 Scenario Outline: I search for Organization endpoint data by ODS Code via APIM with invalid _revinclude value - smoke test
    When I request data from the smoke test APIM endpoint "Organization" with an odscode from dynamo organisation table and params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "The request is missing the '_revinclude=Endpoint:organization' parameter, which is required to include linked Endpoint resources."
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
      | params     |
      |_revinclude=:&identifier=https://fhir.nhs.uk/Id/ods-organization-code         |
      |_revinclude=Invalid:value&identifier=https://fhir.nhs.uk/Id/ods-organization-code      |
      |_revinclude=ENDPOINT:ORGANIZATION&identifier=https://fhir.nhs.uk/Id/ods-organization-code |


  Scenario Outline: I search for Organization endpoint data by ODS Code via APIM with invalid identifier system - smoke test
    When I request data from the smoke test APIM endpoint "Organization" with an odscode from dynamo organisation table and params "<params>"
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
      |_revinclude=Endpoint:organization&identifier=                           |                            |
      |_revinclude=Endpoint:organization&identifier=invalidSystem             | invalidSystem              |
      |_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-codeInvalid| https://fhir.nhs.uk/Id/ods-organization-codeInvalid |


  Scenario Outline: I search for Organization endpoint data by ODS Code via APIM with missing parameters - smoke test
    When I request data from the smoke test APIM endpoint "Organization" with an odscode from dynamo organisation table and params "<params>"
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
    |identifier=https://fhir.nhs.uk/Id/ods-organization-code            | '_revinclude'               |
    |                                                                    | 'identifier', '_revinclude' |


Scenario Outline: I search for Organization endpoint data by ODS Code via APIM with unexpected query parameter - smoke test
    When I request data from the smoke test APIM endpoint "Organization" with an odscode from dynamo organisation table and params "<params>"    
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Unexpected query parameter(s): <unexpected_param>. Only 'identifier' and '_revinclude' are allowed."
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
    |params                                                             | unexpected_param | unexpected_value |
    | _revinclude=Endpoint:organization&foo=bar&identifier=https://fhir.nhs.uk/Id/ods-organization-code | foo              | bar              |
    | _revinclude=Endpoint:organization&_sort=name&identifier=https://fhir.nhs.uk/Id/ods-organization-code | _sort            | name             |


  Scenario Outline: I search for Organization endpoint data by ODS Code via APIM with ODS code at valid boundary length- smoke test
    When I request data from the smoke test APIM endpoint "Organization" with query params "identifier=https://fhir.nhs.uk/Id/ods-organization-code|<ods_code>&_revinclude=Endpoint:organization"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "0" "Organization" resources
    And the bundle contains "0" "Endpoint" resources
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
      | ods_code     |
      | ABCDE        |
      | ABCDE1234567 |

  
    Scenario Outline: I search for Organization endpoint data by ODS Code via APIM with an existing ODS code from the Organisation dynamo table with missing mandatory headers - smoke test
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table with headers "<headers>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "required"
    And the OperationOutcome contains an issue with diagnostics "Missing required header(s): <missing_headers>"
    And the OperationOutcome contains an issue with details for REC_BAD_REQUEST coding

    Examples:
      | headers                    | missing_headers           |
      | {"X-Request-Id": "req_id"} | 'version'                 |
      | {"version": "1"}           | 'x-request-id'            |
      | {}                         | 'version', 'x-request-id' |


  Scenario: I can access APIM for the dos-search 'ping' Endpoint and no access is required - smoke test
    When I request data from the APIM endpoint "_ping" with an odscode from dynamo organisation table but without authentication
    Then I receive a status code "200" in response


  Scenario: I cannot search for Organization endpoint data by ODS Code without mtls credentials - smoke test
    When I attempt to request data from the "dos-search" endpoint "Organization" with an odscode from dynamo organisation table but without authentication
    Then I receive a connection reset error


  Scenario: I cannot search for Organization endpoint data by ODS Code via APIM with invalid access token - smoke test
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table but with invalid token
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding


  Scenario: I cannot search for Organization endpoint data by ODS Code via APIM without authentication - smoke test
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table but without authentication
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding




  Scenario: I cannot search for Organization endpoint data by ODS Code via APIM with malformed Authorization header format - smoke test
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table but with malformed auth header
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding




  Scenario: I cannot search for Organization endpoint data by ODS Code via APIM with empty Authorization header - smoke test
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table but with empty auth header
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding
