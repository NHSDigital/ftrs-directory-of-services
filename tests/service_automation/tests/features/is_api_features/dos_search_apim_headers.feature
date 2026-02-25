@is-apim @integrated-search @dos-search-ods-code-api
@nhsd_apim_authorization(access="application",level="level3")
Feature: API DoS Service validates headers

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"

  Scenario: I cannot search APIM for dos-search Endpoint when missing mandatory headers
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046" with headers "<headers>"
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

  Scenario: I cannot search APIM for dos-search Endpoint with an invalid version
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046" with headers "{"X-Request-Id": "req_id", "version": "2"}"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Invalid version found in supplied headers: version must be '1'"
    And the OperationOutcome contains an issue with details for REC_BAD_REQUEST coding

  Scenario: I cannot search APIM for dos-search Endpoint with an unexpected header
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046" with headers "<headers>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Unexpected header(s): evil-header."
    And the OperationOutcome contains an issue with details for REC_BAD_REQUEST coding
    Examples:
      | headers                                                                                                | 
      | {"X-Request-Id": "req_id", "version": "1", "evil-header": "DROP TABLES"}                               |
      | {"X-Request-Id": "req_id", "version": "1", "evil-header": "DROP TABLES", "End-User-Role": "Clinician"} | 
