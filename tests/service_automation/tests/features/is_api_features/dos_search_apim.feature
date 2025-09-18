@is-api @is-pipeline @gp-search-api
@nhsd_apim_authorization(access="application",level="level3")
Feature: API DoS Service Search APIM

  Background: Set stack and seed repo
    Given that the stack is "gp-search"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"


@test
  Scenario: I search APIM for GP Endpoint by ODS Code with valid query parameters
    When I request data from the APIM "servicesearch" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources
