@etl-ods
Feature: ETL Event Flow - Happy Path
Feature: Ensure messages from Lambda are processed and stored correctly in DynamoDB

  Background:
    Given extract ODS organisation records modified since yesterday
    And extract detailed organisation information for those ODS codes

  Scenario: Organisation data is successfully written to DynamoDB with AWS CloudWatch validation
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json" using specific ODS codes
    When I trigger the ODS ETL pipeline with the valid date
    Then the organisation data should be updated in DynamoDB for "single" ODS codes
