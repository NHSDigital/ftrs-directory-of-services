@is-infra @ftrs-pipeline @is-lambda
Feature: Lambda function

  Background: Check lambda function exists
    Given that the lambda function "dos-search-ods-code-lambda" exists for stack "dos-search"


  Scenario: The lambda returns a response that contains the ods code
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I invoke the lambda with the ods code "M00081046"
    Then the lambda response contains the ods code "M00081046"
    And the lambda response contains the endpoint id "d449e3b8-eba2-43ec-9ee5-aee85387b53d"


#-------------------schema and structure tests-------------------

  Scenario: The lambda returns a valid response against the schema
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I invoke the lambda with the ods code "M00081046"
    Then the lambda response contains a bundle
    And the lambda response contains "1" "Organization" resources
    And the lambda response contains "4" "Endpoint" resources

  Scenario: The Lambda response contains a bundle
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I invoke the lambda with the ods code "M00081046"
    Then the lambda response contains a bundle


  Scenario: The Lambda response contains an organization resource
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I invoke the lambda with the ods code "M00081046"
    Then the lambda response contains "1" "Organization" resources

  Scenario: The Lambda response contains an endpoint resource
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I invoke the lambda with the ods code "M00081046"
    Then the lambda response contains "4" "Endpoint" resources


  Scenario: For an odsCode without Endpoints a bundle containing only an organisazation resource will be returned
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-0-endpoints.json"
    When I invoke the lambda with the ods code "F00081015"
    Then the lambda response contains "0" "Endpoint" resources

  Scenario: For an odsCode that has more than one record only the first record will be returned
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-same-ods-code-2-endpoints.json"
    And I create a model in the repo from json file "Organisation/organisation-with-same-ods-code-0-endpoints.json"
    When I invoke the lambda with the ods code "P00083010"
    Then the lambda response contains the ods code "P00083010"
    And the lambda response contains "1" "Organization" resources
    And the lambda response contains "2" "Endpoint" resources


  Scenario: For an odsCode that does not exist an empty bundle will be returned
    When I invoke the lambda with the ods code "0VE7BPDES6"
    Then the lambda response contains an empty bundle


  Scenario: A lowercase odscode is accepted and returns a response for the same odsCode
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I invoke the lambda with the ods code "m00081046"
    Then the lambda response contains the ods code "M00081046"

#-------------------validation tests------------------


  Scenario: Invoke lambda with an ods code of a length of 12 and a valid response is returned
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-12-character-ods-code.json"
    When I invoke the lambda with the ods code "ABCDEFGHIJ12"
    Then the lambda response contains a bundle
    And the lambda response contains the ods code "ABCDEFGHIJ12"


  Scenario: Invoke lambda with an ods code of a length of 5 and a valid response is returned
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-5-character-ods-code.json"
    When I invoke the lambda with the ods code "E8104"
    Then the lambda response contains the ods code "E8104"
