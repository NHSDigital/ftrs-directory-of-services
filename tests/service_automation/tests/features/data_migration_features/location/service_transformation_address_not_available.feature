@data-migration
Feature: Service Transformation with "Not Available" Address
  As a service directory user
  I want services with "Not Available" address to be migrated without an address field
  So that placeholder values do not appear in the directory

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario Outline: Migrate GP practice with "<case_description>" address value
    Given a 'Service' exists called '<service_name>' in DoS with attributes:
      | key                 | value                      |
      | id                  | <service_id>               |
      | uid                 | <uid>                      |
      | name                | <service_name>             |
      | publicname          | <publicname>               |
      | typeid              | 100                        |
      | statusid            | 1                          |
      | odscode             | <odscode>                  |
      | createdtime         | 2024-01-01 10:00:00        |
      | modifiedtime        | 2024-01-01 10:00:00        |
      | openallhours        | false                      |
      | restricttoreferrals | false                      |
      | postcode            | <postcode>                 |
      | address             | <address_value>            |
      | town                | <town>                     |
      | web                 | https://www.nhs.uk/        |
      | email               | <email>                    |
      | publicphone         | <publicphone>              |
    When a single service migration is run for ID '<service_id>'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    And service ID '<service_id>' was transformed into 1 organisation, 1 location and 1 healthcare service
    And the location for service ID '<service_id>' should have no address

    Examples:
      | case_description | service_id | uid    | service_name        | publicname                  | odscode | address_value | town   | postcode | email         | publicphone    |
      | Not Available    | 24170      | 200030 | TestGPNotAvailable1 | Test Surgery - Not Available 1 | B12350  | Not Available | London | W1A 1AA  | test1@nhs.net | 0300 111 22 33 |
      | not available    | 24171      | 200031 | TestGPNotAvailable2 | Test Surgery - Not Available 2 | B12351  | not available | London | W1A 1AA  | test2@nhs.net | 0300 111 22 34 |
      | NOT AVAILABLE    | 24172      | 200032 | TestGPNotAvailable3 | Test Surgery - Not Available 3 | B12352  | NOT AVAILABLE |        |          | test3@nhs.net | 0300 111 22 35 |
      | NoT aVaIlAbLe    | 24173      | 200033 | TestGPNotAvailable4 | Test Surgery - Not Available 4 | B12353  | NoT aVaIlAbLe | LONDON | SE1 1AA  | test4@nhs.net | 0300 111 22 36 |
