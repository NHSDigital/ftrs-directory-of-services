@data-migration @ftrs-pipeline
Feature: Run Single Service Migration
  As a test author
  I want to execute a data migration for an individual service
  So that I can verify the migration process correctly identifies inactive services and skips them without errors


  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Migrate a single GP practice service inactive
    Given a 'Service' exists called 'TestGPPractice3' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 300002                                     |
      | uid                 | 200002                                     |
      | name                | TestGPPractice3                            |
      | publicname          | The Village Surgery - Westminster Branch   |
      | typeid              | 100                                        |
      | statusid            | 2                                          |
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
    When a single service migration is run for ID '300002'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 0 transformed, 0 migrated, 1 skipped and 0 errors
    And service ID '300002' was skipped due to reason 'Service is not active'
