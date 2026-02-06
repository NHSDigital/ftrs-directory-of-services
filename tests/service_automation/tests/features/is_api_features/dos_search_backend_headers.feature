@is-api @ftrs-pipeline @dos-search-ods-code-api
Feature: API DoS Service Search Backend Gateway Headers

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And the dns for "dos-search" is resolvable
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"


  Scenario Outline: I search for GP Endpoint by ODS Code with valid query parameters and valid headers
    When I request data from the "dos-search" endpoint "Organization" with header "<params>" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources
    Examples:
      |params                        |
      |NHSD-Request-ID=nhsd-req-987654321 |
      |Content-Type=application/fhir+json |
      |NHSD-Correlation-ID=nhsd-corr-123456789 |
      |NHSD-Request-ID=req-987654321 |
      |X-Correlation-ID=x-corr-1122334455 |
      |X-Request-ID=x-req-1122334455|
      |Version=1.0 |
      |End-User-Role=enduserrole-abc123 |
      |Application-ID=appid_12345 |
      |Application-Name=appname-abc123 |
      |Application-ID=appid_12345 |
      |Request-Start-Time=21/01/2026 14:02:23 |
      |Accept-Encoding=gzip, deflate |
      |Accept=application/fhir+json |
      |Accept-Language=en-GB |
      |User-Agent=curl/8.0 |
      |Host= |
      |X-Amzn-Trace-Id=Root=1-67891233-abcdef012345678912345678 |
      |X-Forwarded-For=192.168.1.10 |
      |X-Forwarded-Port=443 |
      |X-Forwarded-Proto=https |
      |NHSD-Request-ID=req-987654321, NHSD-Api-Version=1.0 |


  Scenario: I search for GP Endpoint by ODS Code with valid query parameters and no headers
    When I request data from the "dos-search" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources


  Scenario Outline: I search for GP Endpoint by ODS Code with valid query parameters and invalid headers
    When I request data from the "dos-search" endpoint "Organization" with header "<params>" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome has issues all with severity "error"
    And the OperationOutcome has issues all with code "value"
    And the OperationOutcome contains an issue with diagnostics "Invalid request headers supplied: <header_name>"
    And the OperationOutcome contains an issue with details for REC_BAD_REQUEST coding
    Examples:
      |params                        |header_name           |
      |My-Request-ID=req-987654321   |my-request-id         |
      |Correlation-ID=corr-123456789 |correlation-id        |

