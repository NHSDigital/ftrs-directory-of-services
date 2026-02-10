@is-api @integrated-search @dos-search-ods-code-api
Feature: dos-search tests against the api-gateway to validate the correct handling of headers

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And the dns for "dos-search" is resolvable
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"


  Scenario Outline:I send a request to the dos-search organization endpoint by ODS Code with valid query parameters and valid headers
    When I request data from the "dos-search" endpoint "Organization" with header "<params>" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources
    Examples:
      |params                        |
      |NHSD-Request-ID=req-987654321 |
      |Content-Type=application/fhir+json |
      |NHSD-Correlation-ID=corr-123456789 |
      |NHSD-Request-ID=req-987654321 |
      # |NHSD-Message-Id=msg-1122334455 |
      # |NHSD-Api-Version=1.0 |
      # |NHSD-End-User-Role=GPPracticeAdmin |
      # |NHSD-Client-Id=client-abc123 |
      # |NHSD-Connecting-Party-App-Name=dos-search-service |
      |Accept=application/fhir+json |
      |Accept-Encoding=gzip, deflate |
      |Accept-Language=en-GB |
      |User-Agent=curl/8.0 |
      # |Host=dos-search-ftrs-735.dev.ftrs.cloud.nhs.uk |
      |X-Forwarded-For=192.168.1.10 |
      |X-Forwarded-Port=443 |
      |X-Forwarded-Proto=https |
      |NHSD-Request-ID=req-987654321, NHSD-Api-Version=1.0 |


  Scenario:I send a request to the dos-search organization endpoint by ODS Code with valid query parameters and no headers
    When I request data from the "dos-search" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources


  Scenario Outline:I send a request to the dos-search organization endpoint by ODS Code with valid query parameters and invalid headers
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

