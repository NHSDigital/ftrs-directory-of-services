@data-migration @ftrs-pipeline
Feature: Run Single Service Migration
  As a test author
  I want to run data migration for a single service
  So that I can validate the migration process works correctly

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

    Scenario: Migrate a single GP practice service
      Given a 'Service' exists called 'TestGPPractice' in DoS with attributes:
        | key                 | value                                      |
        | id                  | 300000                                     |
        | uid                 | 200000                                     |
        | name                | The Village Surgery                        |
        | publicname          | The Village Surgery - Westminster Branch   |
        | typeid              | 100                                        |
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
      When a single service migration is run for ID '300000'
      Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
