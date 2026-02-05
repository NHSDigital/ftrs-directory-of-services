@is-api @integrated-search @dos-search-ods-code-api
Feature: API DoS Service Search Backend

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And the dns for "dos-search" is resolvable
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"


  Scenario Outline: I search for GP Endpoint by ODS Code with valid query parameters and valid headers
    When I request data from the "dos-search" endpoint "Organization" with header "<params>" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046"
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



  Scenario: I search for GP Endpoint by ODS Code with valid query parameters and no headers
    When I request data from the "dos-search" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources


@test
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


  Scenario: I search for GP Endpoint by ODS Code with for an ODS code that does not exist
    When I request data from the "dos-search" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|X000081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "0" "Organization" resources
    And the bundle contains "0" "Endpoint" resources

  Scenario Outline: I search for GP Endpoint with invalid ODS code
    When I request data from the "dos-search" endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Invalid identifier value: ODS code '<ods_code>' must follow format ^[A-Za-z0-9]{5,12}$"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | params                                                                                                   | ods_code      |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|&_revinclude=Endpoint:organization              |               |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|0123&_revinclude=Endpoint:organization          | 0123          |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|0123456789ABC&_revinclude=Endpoint:organization | 0123456789ABC |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|123@@@&_revinclude=Endpoint:organization        | 123@@@        |


  Scenario Outline: I search for GP Endpoint with invalid _revinclude value
    When I request data from the "dos-search" endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "The request is missing the '_revinclude=Endpoint:organization' parameter, which is required to include linked Endpoint resources."
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | params                                                                                               |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|M00081046&_revinclude=                      |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|M00081046&_revinclude=Invalid:value         |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|M00081046&_revinclude=ENDPOINT:ORGANIZATION |


  Scenario Outline: I search for GP Endpoint with invalid identifier system
    When I request data from the "dos-search" endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "code-invalid"
    And the OperationOutcome contains an issue with diagnostics "Invalid identifier system '<identifier_system>' - expected 'https://fhir.nhs.uk/Id/ods-organization-code'"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | params                                                                      | identifier_system   |
      | identifier=\|M00081046&_revinclude=Endpoint:organization                    |                     |
      | identifier=invalidSystem\|M00081046&_revinclude=Endpoint:organization       | invalidSystem       |
      | identifier=odsOrganisationCode\|M00081046&_revinclude=Endpoint:organization | odsOrganisationCode |


  Scenario Outline: I search for GP Endpoint with 1 missing parameter
    When I request data from the "dos-search" endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "required"
    And the OperationOutcome contains an issue with diagnostics "Missing required search parameter '<missing_param>'"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | params                                                             | missing_param |
      | identifier=https://fhir.nhs.uk/Id/ods-organization-code\|M00081046 | _revinclude   |
      | _revinclude=Endpoint:organization                                  | identifier    |



  Scenario: I search for GP Endpoint with 2 missing parameters
    When I request data from the "dos-search" endpoint "Organization" with query params ""
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "2" issues
    And the OperationOutcome has issues all with severity "error"
    And the OperationOutcome has issues all with code "required"
    And the OperationOutcome contains an issue with diagnostics "Missing required search parameter 'identifier'"
    And the OperationOutcome contains an issue with diagnostics "Missing required search parameter '_revinclude'"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding


  # New health check scenario for GET /_status
  Scenario: I request a healthcheck of the GP Endpoint and receive a 200 response
    When I request data from the "dos-search" endpoint "_status" with query params ""
    Then I receive a status code "200" in response


  # New error mapping scenarios at the gateway level
  Scenario: I call an endpoint that does not exist and receive a 404 OperationOutcome
    When I request data from the "dos-search" endpoint "DoesNotExist" with query params ""
    Then I receive a status code "404" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "not-supported"
    And the OperationOutcome contains an issue with diagnostics "Unsupported service: /DoesNotExist"
    And the OperationOutcome contains an issue with details for UNSUPPORTED_SERVICE coding




  Scenario Outline: I search for dos-search Endpoint with unexpected query parameter
    When I request data from the "dos-search" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046&<unexpected_param>=<unexpected_value>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Unexpected query parameter(s): <unexpected_param>. Only 'identifier' and '_revinclude' are allowed."
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | unexpected_param | unexpected_value |
      | foo              | bar              |
      | junk             | 123              |
