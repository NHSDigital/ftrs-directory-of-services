@data-migration @incremental-update
Feature: Incremental Updates - Multi-Entity Changes
  Tests for updates that affect multiple FHIR entities simultaneously

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Update affects both Organisation and Healthcare Service entities
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 540001                  |
      | uid                 | 540001                  |
      | name                | Original Service Name   |
      | odscode             | E54001                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 1 Multi Entity Street   |
      | town                | MULTITOWN               |
      | postcode            | MU1 1AA                 |
      | publicphone         | 01234 540001            |
      | email               | multi1@nhs.net          |
      | web                 | www.multi1.com          |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Original Org Name       |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '540001' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#540001' with version 1
    And field 'name' on table 'organisation' for id '28d25ff6-0ada-5024-9666-03cb78f81221' has content:
      """
      {
        "name": "Original Org Name"
      }
      """
    And field 'name' on table 'healthcare-service' for id '9f358116-707f-572b-bce3-7543fa6cb8e7' has content:
      """
      {
        "name": "Original Service Name"
      }
      """

    # Update both service name (affects HealthcareService) and publicname (affects Organisation)
    Given the "Service" with id "540001" is updated with attributes
      | key        | value                |
      | name       | Updated Service Name |
      | publicname | Updated Org Name     |

    When the data migration process is run for table 'services', ID '540001' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#540001' with version 2
    And field 'name' on table 'organisation' for id '28d25ff6-0ada-5024-9666-03cb78f81221' has content:
      """
      {
        "name": "Updated Org Name"
      }
      """
    And field 'name' on table 'healthcare-service' for id '9f358116-707f-572b-bce3-7543fa6cb8e7' has content:
      """
      {
        "name": "Updated Service Name"
      }
      """

  Scenario: Update affects both Healthcare Service and Location entities
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 540002                  |
      | uid                 | 540002                  |
      | name                | Original Service        |
      | odscode             | E54002                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 1 Original Location     |
      | town                | ORIGINALTOWN            |
      | postcode            | OR1 1AA                 |
      | publicphone         | 01234 540002            |
      | email               | multi2@nhs.net          |
      | web                 | www.multi2.com          |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Multi2 Practice         |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '540002' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#540002' with version 1
    And field 'address' on table 'location' for id '1190a981-dee4-5ee2-8a59-17afca9938ce' has content:
      """
      {
        "address": {
          "line1": "1 Original Location",
          "line2": null,
          "county": null,
          "town": "ORIGINALTOWN",
          "postcode": "OR1 1AA"
        }
      }
      """
    And field 'telecom' on table 'healthcare-service' for id 'd38fee28-ece0-53a9-b4c8-cc9630f69fe9' has content:
      """
      {
        "telecom": {
          "phone_public": "01234540002",
          "phone_private": null,
          "email": "multi2@nhs.net",
          "web": "www.multi2.com"
        }
      }
      """

    # Update phone (affects HealthcareService telecom) and address (affects Location)
    Given the "Service" with id "540002" is updated with attributes
      | key         | value                  |
      | publicphone | 01234 999999           |
      | address     | 99 New Location Street |
      | town        | NEWTOWN                |
      | postcode    | NE9 9ZZ                |

    When the data migration process is run for table 'services', ID '540002' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#540002' with version 2
    And field 'address' on table 'location' for id '1190a981-dee4-5ee2-8a59-17afca9938ce' has content:
      """
      {
        "address": {
          "line1": "99 New Location Street",
          "line2": null,
          "county": null,
          "town": "NEWTOWN",
          "postcode": "NE9 9ZZ"
        }
      }
      """
    And field 'telecom' on table 'healthcare-service' for id 'd38fee28-ece0-53a9-b4c8-cc9630f69fe9' has content:
      """
      {
        "telecom": {
          "phone_public": "01234999999",
          "phone_private": null,
          "email": "multi2@nhs.net",
          "web": "www.multi2.com"
        }
      }
      """

  Scenario: Update affects Organisation, Healthcare Service, and Location entities
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 540003                  |
      | uid                 | 540003                  |
      | name                | Original Service Name   |
      | odscode             | E54003                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 1 Original Street       |
      | town                | ORIGINALTOWN            |
      | postcode            | OR3 3AA                 |
      | publicphone         | 01234 540003            |
      | email               | multi3@nhs.net          |
      | web                 | www.multi3.com          |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Original Org            |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '540003' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#540003' with version 1
    And field 'name' on table 'organisation' for id 'df73a0f1-4d7a-53df-86e0-d0f2a17e6734' has content:
      """
      {
        "name": "Original Org"
      }
      """
    And field 'positionGCS' on table 'location' for id 'afaf7a1c-f844-5851-9c98-2179004cfe81' has content:
      """
      {
        "positionGCS": {
          "latitude": "51.5074000000",
          "longitude": "-0.1278000000"
        }
      }
      """
    And field 'name' on table 'healthcare-service' for id '71009484-e6c2-51fc-ad99-31277deed002' has content:
      """
      {
        "name": "Original Service Name"
      }
      """

    # Comprehensive update affecting all entities
    Given the "Service" with id "540003" is updated with attributes
      | key         | value                |
      | publicname  | Updated Org          |
      | name        | Updated Service Name |
      | publicphone | 01234 888888         |
      | email       | newemail@nhs.net     |
      | address     | 99 Updated Avenue    |
      | town        | UPDATEDTOWN          |
      | postcode    | UP9 9ZZ              |
      | latitude    | 53.4808              |
      | longitude   | -2.2426              |

    When the data migration process is run for table 'services', ID '540003' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#540003' with version 2
    And field 'name' on table 'organisation' for id 'df73a0f1-4d7a-53df-86e0-d0f2a17e6734' has content:
      """
      {
        "name": "Updated Org"
      }
      """
    And field 'positionGCS' on table 'location' for id 'afaf7a1c-f844-5851-9c98-2179004cfe81' has content:
      """
      {
        "positionGCS": {
          "latitude": "53.4808000000",
          "longitude": "-2.2426000000"
        }
      }
      """
    And field 'name' on table 'healthcare-service' for id '71009484-e6c2-51fc-ad99-31277deed002' has content:
      """
      {
        "name": "Updated Service Name"
      }
      """
