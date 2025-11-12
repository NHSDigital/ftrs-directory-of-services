@data-migration @ftrs-pipeline
Feature: Run Single Service Migration
  As a test author
  I want to execute a data migration for an individual service
  So that I can confirm the migration process correctly identifies unsupported cases and handles them gracefully without errors

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Migrate a single GP practice service no transformer found
    Given a 'Service' exists called 'TestGPPractice2' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 300001                                     |
      | uid                 | 200001                                     |
      | name                | TestGPPractice2                            |
      | publicname          | The Village Surgery - Westminster Branch   |
      | typeid              | 12                                         |
      | statusid            | 1                                          |
      | odscode             | A12345                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            | SW1A 1AA                                   |
      | address             | Westminster                                |
      | town                | London                                     |
      | web                 | https://www.nhs.uk/                        |
      | email               | england.contactus@nhs.net                  |
      | publicphone         | 0300 311 22 33                             |
    When a single service migration is run for ID '300001'
    Then the metrics should be 1 total, 0 supported, 1 unsupported, 0 transformed, 0 migrated, 0 skipped and 0 errors
    And service ID '300001' was not migrated due to reason 'No suitable transformer found'
