Feature: DoS Data Manipulation
  As a test author
  I need to be able to create and modify DoS data in the test database
  So that I can test different scenarios in the data migration pipeline

  Scenario: Create a basic service in DoS
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 300000                      |
      | uid                 | 200000                      |
      | name                | GP - Some Place, Some Town  |
      | typeid              | 13                          |
      | statusid            | 1                           |
      | createdtime         | 2024-01-01 10:00:00         |
      | modifiedtime        | 2024-01-01 10:00:00         |
      | openallhours        | false                       |
      | restricttoreferrals | false                       |
      | postcode            | AB1 2CD                     |
      | address             | 123 Some Street             |
      | town                | Some Town                   |
      | web                 | https://www.nhs.uk/         |
      | email               | england.contactus@nhs.net   |
      | publicphone         | 0300 311 22 33              |
    When I query the "services" table for "id" "300000"
    Then the record should exist in the database
    And the "uid" field should be "200000"
    And the "name" field should be "GP - Some Place, Some Town"
    And the "typeid" field should be "13"
    And the "statusid" field should be "1"
    And the "createdtime" field should be "2024-01-01 10:00:00"
    And the "modifiedtime" field should be "2024-01-01 10:00:00"
    And the "openallhours" field should be "false"
    And the "restricttoreferrals" field should be "false"
    And the "postcode" field should be "AB1 2CD"
    And the "address" field should be "123 Some Street"
    And the "town" field should be "Some Town"
    And the "web" field should be "https://www.nhs.uk/"
    And the "email" field should be "england.contactus@nhs.net"
    And the "publicphone" field should be "0300 311 22 33"

  Scenario: Update an existing service name
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 300001                      |
      | uid                 | 200001                      |
      | name                | Original Service Name       |
      | typeid              | 13                          |
      | statusid            | 1                           |
      | createdtime         | 2024-01-01 10:00:00         |
      | modifiedtime        | 2024-01-01 10:00:00         |
      | openallhours        | false                       |
      | restricttoreferrals | false                       |
    When I query the "services" table for "id" "300001"
    Then the record should exist in the database
    And the "name" field should be "Original Service Name"
    Given the "Service" with id "300001" is updated with attributes
      | key          | value                       |
      | name         | Updated Service Name        |
      | modifiedtime | 2024-01-02 10:00:00         |
    When I query the "services" table for "id" "300001"
    Then the record should exist in the database
    And the "name" field should be "Updated Service Name"

    Scenario: Create service with related entities
    Given a "Service" exists in DoS with attributes
      | key                 | value          |
      | id                  | 300002         |
      | uid                 | 200002         |
      | name                | Parent Service |
      | typeid              | 13             |
      | openallhours        | false          |
      | restricttoreferrals | false          |
    And a "ServiceAgeRange" exists in DoS with attributes
      | key       | value       |
      | id        | 1000000     |
      | serviceid | 300002      |
      | daysfrom  | 0           |
      | daysto    | 365         |
    When I query the "services" table for "id" "300002"
    Then the record should exist in the database
    When I query the "service_age_ranges" table for "id" "1000000"
    Then the record should exist in the database
    And the "daysfrom" field should be "0"
    And the "daysto" field should be "365"

  Scenario Outline: Create and verify service with different data sets
    Given a "Service" exists in DoS with attributes
      | key                 | value              |
      | id                  | <service_id>       |
      | uid                 | <uid>              |
      | name                | <name>             |
      | typeid              | 13                 |
      | statusid            | 1                  |
      | createdtime         | 2024-01-01 10:00:00|
      | modifiedtime        | 2024-01-01 10:00:00|
      | openallhours        | false              |
      | restricttoreferrals | false              |
    When I query the "services" table for "id" "<service_id>"
    Then the record should exist in the database
    And the "uid" field should be "<uid>"
    And the "name" field should be "<name>"

    Examples:
      | service_id | uid    | name                        |
      | 300000     | 200000 | GP - Some Place, Some Town  |
      | 300001     | 200001 | Hospital - Another Location |
      | 300002     | 200002 | Pharmacy - City Centre      |
      | 300003     | 200003 | Dental Practice             |
