@is-infra @is-pipeline @is-lambda
Feature: Lambda function

  Background: Check lambda function exists
    Given that the lambda function "gp-search-lambda" exists for stack "gp-search"


  Scenario: The lambda returns a response that contains the ods code
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/36fce427-0f31-4a4e-903f-74dcf9e63cfd.json"
    When I invoke the lambda with the ods code "M00081046"
    Then the lambda response contains the ods code "M00081046"
    And the lambda response contains the endpoint id "d449e3b8-eba2-43ec-9ee5-aee85387b53d"


#-------------------schema and structure tests-------------------

  Scenario: The lambda returns a valid response against the schema
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/36fce427-0f31-4a4e-903f-74dcf9e63cfd.json"
    When I invoke the lambda with the ods code "M00081046"
    Then the lambda response contains a bundle
    And the lambda response contains "1" "Organization" resources
    And the lambda response contains "4" "Endpoint" resources

  Scenario: The Lambda response contains a bundle
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/1481a74c-8dd3-4b5b-bca5-dd1701f25b09.json"
    When I invoke the lambda with the ods code "N00081063"
    Then the lambda response contains a bundle


  Scenario: The Lambda response contains an organization resource
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/1481a74c-8dd3-4b5b-bca5-dd1701f25b09.json"
    When I invoke the lambda with the ods code "N00081063"
    Then the lambda response contains "1" "Organization" resources

  Scenario: The Lambda response contains an endpoint resource
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/1481a74c-8dd3-4b5b-bca5-dd1701f25b09.json"
    When I invoke the lambda with the ods code "N00081063"
    Then the lambda response contains "4" "Endpoint" resources


  Scenario: For an odsCode without Endpoints a bundle containing only an organisazation resource will be returned
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/377dbc2b-b2f9-4d14-9cc5-5360752b3a6c.json"
    When I invoke the lambda with the ods code "F00081015"
    Then the lambda response contains "0" "Endpoint" resources

  Scenario: For an odsCode that has more than one record only the first record will be returned
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/6ed15508-e2dc-4adc-8349-35224d8903f9.json"
    When I invoke the lambda with the ods code "P00083010"
    Then the lambda response contains the ods code "P00083010"
    And the lambda response contains "1" "Organization" resources
    And the lambda response contains "2" "Endpoint" resources


  Scenario: For an odsCode that does not exist an empty bundle will be returned
    When I invoke the lambda with the ods code "12345"
    Then the lambda response contains an empty bundle


  Scenario: A lowercase odscode is accepted and returns a response for the same odsCode
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/6ed15508-e2dc-4adc-8349-35224d8903f9.json"
    When I invoke the lambda with the ods code "p00083010"
    Then the lambda response contains the ods code "P00083010"

#-------------------validation tests------------------


  Scenario: Invoke lambda with an ods code of a length of 12 and a valid response is returned
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/22d9d655-2019-42c4-b890-acc808de3f84.json"
    When I invoke the lambda with the ods code "ABCDEFGHIJ12"
    Then the lambda response contains a bundle
    And the lambda response contains the ods code "ABCDEFGHIJ12"


  Scenario: Invoke lambda with an ods code of a length of 5 and a valid response is returned
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/315809be-33ab-46b2-850c-f81e3ec0366b.json"
    When I invoke the lambda with the ods code "E8104"
    Then the lambda response contains the ods code "E8104"


  Scenario: Invoke lambda with an ods code set to "" and a validation error is returned
    When I invoke the lambda with the ods code ""
    Then the lambda returns the status code "422"
    And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
    And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
    And the lambda returns the diagnostics "Value error, ODS code must be at least 5 characters long"


  Scenario: Invoke lambda with an ods code of a length of 13 and a validation error is returned
    When I invoke the lambda with the ods code "ABCDEFGHIJKLM"
    Then the lambda returns the status code "422"
    And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
    And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
    And the lambda returns the diagnostics "Value error, ODS code must be at most 12 characters long"


  Scenario: Invoke lambda with an ods code of a length of 4 and a validation error is returned
    When I invoke the lambda with the ods code "ABCD"
    Then the lambda returns the status code "422"
    And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
    And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
    And the lambda returns the diagnostics "Value error, ODS code must be at least 5 characters long"


  Scenario: Invoke lambda with an ods code containing special characters and a validation error is returned
    When I invoke the lambda with the ods code "P00083010@"
    Then the lambda returns the status code "422"
    And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
    And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
    And the lambda returns the diagnostics "Value error, ODS code must contain only letters and numbers"

