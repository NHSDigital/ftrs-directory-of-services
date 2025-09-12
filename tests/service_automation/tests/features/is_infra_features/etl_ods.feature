@ds-infra @ds-pipeline @etl-ods
Feature: ETL Event Flow
Feature: Ensure messages from Lambda are processed and stored correctly in DynamoDB

  Background:
    Given extract ODS organisation records modified since yesterday
    And extract detailed organisation information for those ODS codes

  Scenario: Organisation data is successfully written to DynamoDB with AWS CloudWatch validation
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json" using specific ODS codes
    When I invoke the lambda with the valid date
    And the Lambda extracts, transforms, and publishes the transformed message to SQS
    # And the consumer calls the CRUD API through APIM
    Then the organisation data should be updated in DynamoDB for the specified ODS codes
                |





