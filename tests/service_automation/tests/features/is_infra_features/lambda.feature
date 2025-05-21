@is-infra @is-pipeline @is-lambda
Feature: Lambda function

Background: Check lambda function exists
  Given that the lambda function "gp-search-lambda" exists for stack "gp-search"


  Scenario: The lambda returns a response that contains the ods code
  When I invoke the lambda with the ods code "P83010"
  Then the lambda response contains the ods code "P83010"


  Scenario: The lambda returns a valid response against the schema
  When I invoke the lambda with the ods code "P83010"
  Then the response is valid against the schema
  And the lambda response contains a bundle
  And the lambda response contains an organization resource
  And the lambda response contains an endpoint resource

  Scenario: The Lambda response contains a bundle
  When I invoke the lambda with the ods code "P83010"
  Then the lambda response contains a bundle

  Scenario: The Lambda response contains an organization resource
  When I invoke the lambda with the ods code "P83010"
  Then the lambda response contains an organization resource


  Scenario: The Lambda response contains an endpoint resource
  When I invoke the lambda with the ods code "P83010"
  Then the lambda response contains an endpoint resource


  Scenario: For an odsCode without Endpoints a bundle containing only an organisazation resource will be returned
  When I invoke the lambda with the ods code "F81015"
  Then the lambda response does not contain an endpoint resource


  Scenario: For an odsCode that has more than one record only the first record will be returned
  When I invoke the lambda with the ods code "P83010"
  Then the lambda response contains the ods code "P83010"
  And the lambda response contains only "1" organization resource
  And the lambda response contains "2" endpoint resource


  Scenario: A lowercase odscode is accepted and returns the a response for the same odsCode
  When I invoke the lambda with the ods code "p83010"
  Then the lambda response contains the ods code "P83010"


  Scenario: For an odsCode that does not exist an empty bundle will be returned
  When I invoke the lambda with the ods code "12345"
  Then the lambda response contains an empty bundle

  Scenario: Invoke lambda with an ods code set to "" and a validation error is returned
  When I invoke the lambda with the ods code value not set
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Failed schema validation. Error: data.odsCode must be longer than or equal to 5 characters, Path: ['data', 'odsCode'], Data: "


  Scenario: Invoke lambda with an ods code of a length of 13 and a validation error is returned
  When I invoke the lambda with the ods code "ABCDEFGHIJKLM"
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Failed schema validation. Error: data.odsCode must be shorter than or equal to 12 characters, Path: ['data', 'odsCode'], Data: ABCDEFGHIJKLM"


  Scenario: Invoke lambda with an ods code of a length of 4 and a validation error is returned
  When I invoke the lambda with the ods code "ABCD"
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Failed schema validation. Error: data.odsCode must be longer than or equal to 5 characters, Path: ['data', 'odsCode'], Data: ABCD"


  Scenario: Invoke lambda with an ods code containing special characters and a validation error is returned
  When I invoke the lambda with the ods code "P83010@"
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Failed schema validation. Error: data.odsCode must match pattern ^[A-Z0-9]+$, Path: ['data', 'odsCode'], Data: P83010@"


  Scenario: Invoke lambda with an empty event and a validation error is returned
  When I invoke the lambda with an empty event
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Failed schema validation. Error: data must contain ['odsCode'] properties, Path: ['data'], Data: {}"

