@is-apim @integrated-search @dos-search-ods-code-api
@nhsd_apim_authorization(access="application",level="level3")
Feature: dos-search tests to validate the response structure from the api-gateway and APIM

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And the dns for "dos-search" is resolvable
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"

  Scenario: I search for Organization endpoint data by ODS Code and verify all response values match the expected test data for organisation M00081046
    When I request data from the "dos-search" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046"
    Then I receive a status code "200" in response
    And the response headers contain "Content-Type" with value "application/fhir+json"

    # Bundle structure validation
    And the response body contains a bundle
    And the bundle type is "searchset"
    And the bundle contains a self link
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources

    # Search modes validation
    And all "Organization" entries have search mode "match"
    And all "Endpoint" entries have search mode "include"

    # Organization resource fields validation
    And the "Organization" resource has "identifier" array containing "use" with value "official"
    And the "Organization" resource has "identifier" array containing "system" with value "https://fhir.nhs.uk/Id/ods-organization-code"
    And the "Organization" resource has "identifier" array containing "value" with value "M00081046"
    And the "Organization" resource has "name" field with value "Abbottswood Medical Practice, Pershore, Worcestershire"
    And the "Organization" resource has "active" field with boolean true
    And the "Organization" resource identifier value matches ODS code pattern

    # All Endpoints structure validation
    And all Endpoint resources have status in ["active"]
    And all Endpoint resources have connectionType with system and code
    And all Endpoint resources have managingOrganization reference
    And all Endpoint managingOrganization references point to the parent Organization
    And all Endpoint resources have payloadType array
    And all Endpoint resources have payloadMimeType array
    And all Endpoint resources have address field

    # Endpoint extensions validation
    And all Endpoint resources have extension OrganizationEndpointOrder as integer
    And all Endpoint resources have extension EndpointCompression as boolean
    And all Endpoint resources have extension EndpointBusinessScenario with valid values

    # Schema validation
    And the response is valid against the dos-search schema for endpoint "/Organization"

  Scenario: I search for Organization endpoint data by ODS Code and verify the Bundle structure of a successful response conforms to the specification
    When I request data from the "dos-search" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle type is "searchset"
    And the bundle contains a self link
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources
    And all "Organization" entries have search mode "match"
    And all "Endpoint" entries have search mode "include"
    And the response headers contain "Content-Type" with value "application/fhir+json"
    And the response is valid against the dos-search schema for endpoint "/Organization"



  Scenario: I search for Organization endpoint data by ODS Code and verify individual endpoint data values for organisation M00081046
    When I request data from the "dos-search" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=https://fhir.nhs.uk/Id/ods-organization-code|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "4" "Endpoint" resources

    # Endpoint 0 - Email Primary GP Recipient (order 2)
    And Endpoint 0 has "status" with value "active"
    And Endpoint 0 has "connectionType.code" with value "email"
    And Endpoint 0 has "address" with value "dummy-endpoint-email@nhs.net"
    And Endpoint 0 has "payloadMimeType" containing "application/pdf"
    And Endpoint 0 has extension "OrganizationEndpointOrder" with valueInteger 2
    And Endpoint 0 has extension "EndpointCompression" with valueBoolean false
    And Endpoint 0 has extension "EndpointBusinessScenario" with valueCode "primary-recipient"

    # Endpoint 1 - Email Copy Recipient (order 2)
    And Endpoint 1 has "status" with value "active"
    And Endpoint 1 has "connectionType.code" with value "email"
    And Endpoint 1 has "address" with value "dummy-endpoint-email@nhs.net"
    And Endpoint 1 has "payloadMimeType" containing "application/pdf"
    And Endpoint 1 has extension "OrganizationEndpointOrder" with valueInteger 2
    And Endpoint 1 has extension "EndpointCompression" with valueBoolean false
    And Endpoint 1 has extension "EndpointBusinessScenario" with valueCode "copy-recipient"

    # Endpoint 2 - ITK Copy Recipient (order 1)
    And Endpoint 2 has "status" with value "active"
    And Endpoint 2 has "connectionType.code" with value "itk"
    And Endpoint 2 has "address" with value "https://dummy-itk-endpoint.nhs.uk"
    And Endpoint 2 has "payloadMimeType" containing "application/hl7-cda+xml"
    And Endpoint 2 has extension "OrganizationEndpointOrder" with valueInteger 1
    And Endpoint 2 has extension "EndpointCompression" with valueBoolean false
    And Endpoint 2 has extension "EndpointBusinessScenario" with valueCode "copy-recipient"

    # Endpoint 3 - ITK Primary GP Recipient (order 1)
    And Endpoint 3 has "status" with value "active"
    And Endpoint 3 has "connectionType.code" with value "itk"
    And Endpoint 3 has "address" with value "https://dummy-itk-endpoint.nhs.uk"
    And Endpoint 3 has "payloadMimeType" containing "application/hl7-cda+xml"
    And Endpoint 3 has extension "OrganizationEndpointOrder" with valueInteger 1
    And Endpoint 3 has extension "EndpointCompression" with valueBoolean false
    And Endpoint 3 has extension "EndpointBusinessScenario" with valueCode "primary-recipient"


