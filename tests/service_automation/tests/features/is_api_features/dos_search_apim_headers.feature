@is-apim @integrated-search @dos-search-ods-code-api
@nhsd_apim_authorization(access="application",level="level3")

Feature: dos-search tests to validate headers required by the apim proxy and api-gateway

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"


  Scenario Outline: I cannot search for Organization endpoint data by ODS Code when missing mandatory headers
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

  Scenario: I cannot search for Organization endpoint data by ODS Code with an invalid version
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046" with headers "{"X-Request-Id": "req_id", "version": "2"}"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Invalid version found in supplied headers: version must be '1'"
    And the OperationOutcome contains an issue with details for REC_BAD_REQUEST coding

  Scenario Outline: I cannot search for Organization endpoint data by ODS Code with an unexpected header
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


Scenario Outline: I search for Organization endpoint data by ODS Code with valid header and verify it is mirrored back in response headers
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046" with headers "<headers>"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the response headers contain the following headers and values "<response headers>"
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
    |headers                                                                 |response headers                                                                 |
    |{"Version": "1", "X-Correlation-ID": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA", "X-Request-ID": "0E0B220-8136-4CA5-AE46-1D97EF59D068", "Content-Type": "application/fhir+json"} |{"x-correlation-id": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA", "x-request-id": "0E0B220-8136-4CA5-AE46-1D97EF59D068", "content-type": "application/fhir+json"} |


  Scenario Outline: I search for Organization endpoint data by ODS Code with valid UUID formats for X-Request-ID
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046" with headers "{"X-Request-Id": "<valid_uuid>", "version": "1"}"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the response headers contain "x-request-id" with value "<valid_uuid>"
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
      | valid_uuid                            |
      | 60E0B220-8136-4CA5-AE46-1D97EF59D068  |
      | 12345678-1234-1234-1234-123456789012  |
      | ffffffff-ffff-ffff-ffff-ffffffffffff  |
      | FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF  |
      | 12345678-90ab-cdef-1234-567890abcdef  |



  Scenario Outline: I search for Organization endpoint data by ODS Code with valid query parameters and valid headers
    When I request data from the APIM endpoint "Organization" with valid query params and additional headers "<headers>"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources
    Examples:
      |headers                        |
      |{"NHSD-Request-ID": "req-987654321"} |
      |{"Content-Type": "application/fhir+json"} |
      |{"NHSD-Correlation-ID": "corr-123456789"} |
      |{"End-User-Role": "GPPracticeAdmin"} |
      |{"Accept": "application/fhir+json"} |
      |{"Accept-Encoding": "gzip, deflate"} |
      |{"Accept-Language": "en-GB"} |
      |{"User-Agent": "curl/8.0"} |
      |{"X-Forwarded-For": "192.168.1.10"} |
      |{"X-Forwarded-Port": "443"} |
      |{"X-Forwarded-Proto": "https"} |
      |{"NHSD-Request-ID": "req-987654321", "NHSD-Correlation-ID": "corr-123456789"} |


  Scenario Outline: I search for Organization endpoint data by ODS Code with valid query parameters and invalid headers
    When I request data from the APIM endpoint "Organization" with valid query params and additional headers "<headers>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome has issues all with severity "error"
    And the OperationOutcome has issues all with code "value"
    And the OperationOutcome contains an issue with diagnostics "Unexpected header(s): <header_name>."
    And the OperationOutcome contains an issue with details for REC_BAD_REQUEST coding
    Examples:
      |headers                              |header_name           |
      |{"My-Request-ID": "req-987654321"}   |my-request-id         |
      |{"Correlation-ID": "corr-123456789"} |correlation-id        |



Scenario Outline: I search for Organization endpoint data by ODS Code with valid headers in upper and lower case
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046" with headers "<headers>"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the response headers contain the following headers and values "<response headers>"
    And the response is valid against the dos-search schema for endpoint "/Organization"
    Examples:
    |headers                                                                 |response headers                                                                 |
    |{"Version": "1", "X-Correlation-ID": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA", "X-Request-ID": "0E0B220-8136-4CA5-AE46-1D97EF59D068", "Content-Type": "application/fhir+json"} |{"x-correlation-id": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA", "x-request-id": "0E0B220-8136-4CA5-AE46-1D97EF59D068", "content-type": "application/fhir+json"} |
    |{"version": "1", "x-Correlation-iD": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA", "x-ReQuest-id": "0E0B220-8136-4CA5-AE46-1D97EF59D068", "Content-Type": "application/fhir+json"} |{"x-correlation-id": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA", "x-request-id": "0E0B220-8136-4CA5-AE46-1D97EF59D068", "content-type": "application/fhir+json"} |


Scenario Outline: I search for Organization endpoint data by ODS Code via api-g with invalid headers
    When I request data from the "dos-search" endpoint "Organization" with valid query params and invalid headers "<headers>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "2" issues
    And the OperationOutcome has issues all with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Unexpected header(s): <unexpected_header>."
    And the OperationOutcome contains an issue with code "required"
    And the OperationOutcome contains an issue with diagnostics "Missing required header(s): '<missing_headers>'"
    And the OperationOutcome contains an issue with details for REC_BAD_REQUEST coding
    Examples:
      |headers                                    |unexpected_header           |missing_headers           |
      |{"MyVersion": "1", "X-Correlation-ID": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA", "NHSD-Request-ID": "0E0B220-8136-4CA5-AE46-1D97EF59D068"} |myversion       |version|
      |{"version": "1", "x-Correlation-iD": "11C46F5F-CDEF-4865-94B2-0EE0EDCC26DA", "x-ReQuest-id": "0E0B220-8136-4CA5-AE46-1D97EF59D068", "Some-Content-Type": "application/fhir+json"} |some-content-type|x-request-id|
