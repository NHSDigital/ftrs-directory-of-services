@is-apim @integrated-search @dos-search-ods-code-api
@nhsd_apim_authorization(access="application",level="level3")
Feature: API DoS Service validates headers
# Add tests to check that the headers are not case sensitive
# Add tests to check for valid and invalid headers combos are handled correctly
# Add tests that allowed headers are allowed  0 check for differences between apim and apig



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


Scenario Outline: I send a request to the dos-search organization endpoint by ODS Code via APIM with valid header and verify it is mirrored back in response headers
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046" with headers "<headers>"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the response headers contain the following headers and values "<response headers>"
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
    |headers                                                                 |response headers                                                                 |
    |{"Version": "1", "X-Correlation-ID": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA", "X-Request-ID": "0E0B220-8136-4CA5-AE46-1D97EF59D068", "Content-Type": "application/fhir+json"} |{"X-Correlation-ID": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA", "X-Request-ID": "0E0B220-8136-4CA5-AE46-1D97EF59D068", "Content-Type": "application/fhir+json"} |



  Scenario Outline:I send a request via APIM with valid UUID formats for X-Request-ID
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046" with headers "{"X-Request-Id": "<valid_uuid>", "version": "1"}"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the response headers contain "X-Request-ID" with value "<valid_uuid>"
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
      | valid_uuid                            |
      | 60E0B220-8136-4CA5-AE46-1D97EF59D068  |
      | 12345678-1234-1234-1234-123456789012  |
      | ffffffff-ffff-ffff-ffff-ffffffffffff  |
      | FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF  |
      | 12345678-90ab-cdef-1234-567890abcdef  |
