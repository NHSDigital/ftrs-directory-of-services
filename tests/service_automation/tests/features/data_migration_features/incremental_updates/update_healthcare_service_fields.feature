@data-migration @incremental-update
Feature: Incremental Updates - Healthcare Service Field Changes
  Tests for verifying incremental updates to Healthcare Service entity fields

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Update healthcare service name
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 510001                  |
      | uid                 | 510001                  |
      | name                | Original Service Name   |
      | odscode             | B51001                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 10 Service Street       |
      | town                | SERVICETOWN             |
      | postcode            | SE1 1AA                 |
      | publicphone         | 01234 444444            |
      | email               | service1@nhs.net        |
      | web                 | www.service1.com        |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Original Practice       |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '510001' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510001' with version 1
    And field 'name' on table 'healthcare-service' for id '05683161-e3b2-549e-b63c-b7978b677c45' has content:
      """
      {
        "name": "Original Service Name"
      }
      """


    Given the "Service" with id "510001" is updated with attributes
      | key  | value                |
      | name | Updated Service Name |

    When the data migration process is run for table 'services', ID '510001' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510001' with version 2
    And field 'name' on table 'healthcare-service' for id '05683161-e3b2-549e-b63c-b7978b677c45' has content:
      """
      {
        "name": "Updated Service Name"
      }
      """

  Scenario: Update healthcare service phone number
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 510002                  |
      | uid                 | 510002                  |
      | name                | Phone Update Practice   |
      | odscode             | B51002                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 11 Service Street       |
      | town                | SERVICETOWN             |
      | postcode            | SE1 2AA                 |
      | publicphone         | 01234 555555            |
      | email               | service2@nhs.net        |
      | web                 | www.service2.com        |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Phone Update Practice   |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '510002' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510002' with version 1
    And field 'telecom' on table 'healthcare-service' for id '220182b7-d92e-56db-9341-0630f499fdc0' has content:
      """
      {
        "telecom": {
          "email": "service2@nhs.net",
          "phone_public": "01234555555",
          "phone_private": null,
          "web": "www.service2.com"
        }
      }
      """

    Given the "Service" with id "510002" is updated with attributes
      | key         | value        |
      | publicphone | 01234 999888 |

    When the data migration process is run for table 'services', ID '510002' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510002' with version 2
    And field 'telecom' on table 'healthcare-service' for id '220182b7-d92e-56db-9341-0630f499fdc0' has content:
      """
      {
        "telecom": {
          "email": "service2@nhs.net",
          "phone_public": "01234999888",
          "phone_private": null,
          "web": "www.service2.com"
        }
      }
      """

  Scenario: Update healthcare service email
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 510003                  |
      | uid                 | 510003                  |
      | name                | Email Update Practice   |
      | odscode             | B51003                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 12 Service Street       |
      | town                | SERVICETOWN             |
      | postcode            | SE1 3AA                 |
      | publicphone         | 01234 666666            |
      | email               | old.email@nhs.net       |
      | web                 | www.service3.com        |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Email Update Practice   |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '510003' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510003' with version 1
    And field 'telecom' on table 'healthcare-service' for id 'b18551bf-ad82-5428-97d0-9d57ed536242' has content:
      """
      {
        "telecom": {
          "email": "old.email@nhs.net",
          "phone_public": "01234666666",
          "phone_private": null,
          "web": "www.service3.com"
        }
      }
      """

    Given the "Service" with id "510003" is updated with attributes
      | key   | value             |
      | email | new.email@nhs.net |

    When the data migration process is run for table 'services', ID '510003' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510003' with version 2
    And field 'telecom' on table 'healthcare-service' for id 'b18551bf-ad82-5428-97d0-9d57ed536242' has content:
      """
      {
        "telecom": {
          "email": "new.email@nhs.net",
          "phone_public": "01234666666",
          "phone_private": null,
          "web": "www.service3.com"
        }
      }
      """

  Scenario: Update healthcare service website
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 510004                  |
      | uid                 | 510004                  |
      | name                | Website Update Practice |
      | odscode             | B51004                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 13 Service Street       |
      | town                | SERVICETOWN             |
      | postcode            | SE1 4AA                 |
      | publicphone         | 01234 777777            |
      | email               | service4@nhs.net        |
      | web                 | www.oldwebsite.com      |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Website Update Practice |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '510004' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510004' with version 1
    And field 'telecom' on table 'healthcare-service' for id 'f657c502-f229-5910-b85d-dc141ec6835a' has content:
      """
      {
        "telecom": {
          "email": "service4@nhs.net",
          "phone_public": "01234777777",
          "phone_private": null,
          "web": "www.oldwebsite.com"
        }
      }
      """

    Given the "Service" with id "510004" is updated with attributes
      | key | value              |
      | web | www.newwebsite.com |

    When the data migration process is run for table 'services', ID '510004' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510004' with version 2
    And field 'telecom' on table 'healthcare-service' for id 'f657c502-f229-5910-b85d-dc141ec6835a' has content:
      """
      {
        "telecom": {
          "email": "service4@nhs.net",
          "phone_public": "01234777777",
          "phone_private": null,
          "web": "www.newwebsite.com"
        }
      }
      """

  Scenario: Update multiple telecom fields simultaneously
    Given a "Service" exists in DoS with attributes
      | key                 | value                         |
      | id                  | 510005                        |
      | uid                 | 510005                        |
      | name                | Multi Telecom Update Practice |
      | odscode             | B51005                        |
      | openallhours        | FALSE                         |
      | restricttoreferrals | FALSE                         |
      | address             | 14 Service Street             |
      | town                | SERVICETOWN                   |
      | postcode            | SE1 5AA                       |
      | publicphone         | 01234 111111                  |
      | nonpublicphone      | 09876 222222                  |
      | email               | old@nhs.net                   |
      | web                 | www.old.com                   |
      | createdtime         | 2024-01-01 08:00:00.000       |
      | modifiedtime        | 2024-01-01 08:00:00.000       |
      | typeid              | 100                           |
      | statusid            | 1                             |
      | publicname          | Multi Telecom Practice        |
      | latitude            | 51.5074                       |
      | longitude           | -0.1278                       |

    When the data migration process is run for table 'services', ID '510005' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510005' with version 1
    And field 'telecom' on table 'healthcare-service' for id 'acac0887-1086-510d-a4aa-98ec3155a6f1' has content:
      """
      {
        "telecom": {
          "email": "old@nhs.net",
          "phone_public": "01234111111",
          "phone_private": "09876222222",
          "web": "www.old.com"
        }
      }
      """

    Given the "Service" with id "510005" is updated with attributes
      | key            | value               |
      | publicphone    | 01234 999999        |
      | nonpublicphone | 09876 888888        |
      | email          | new@nhs.net         |
      | web            | www.new.com         |
      | modifiedtime   | 2024-06-01 10:00:00 |

    When the data migration process is run for table 'services', ID '510005' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510005' with version 2
    And field 'telecom' on table 'healthcare-service' for id 'acac0887-1086-510d-a4aa-98ec3155a6f1' has content:
      """
      {
        "telecom": {
          "email": "new@nhs.net",
          "phone_public": "01234999999",
          "phone_private": "09876888888",
          "web": "www.new.com"
        }
      }
      """

  Scenario: Add email where none existed before
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 510006                  |
      | uid                 | 510006                  |
      | name                | Add Email Practice      |
      | odscode             | B51006                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 15 Service Street       |
      | town                | SERVICETOWN             |
      | postcode            | SE1 6AA                 |
      | publicphone         | 01234 888888            |
      | email               |                         |
      | web                 | www.addemail.com        |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Add Email Practice      |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '510006' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510006' with version 1
    And field 'telecom' on table 'healthcare-service' for id '1707890d-ec3c-5d2d-8e14-28826dc07c3c' has content:
      """
      {
        "telecom": {
          "email": null,
          "phone_public": "01234888888",
          "phone_private": null,
          "web": "www.addemail.com"
        }
      }
      """

    Given the "Service" with id "510006" is updated with attributes
      | key   | value              |
      | email | newlyadded@nhs.net |

    When the data migration process is run for table 'services', ID '510006' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510006' with version 2
    And field 'telecom' on table 'healthcare-service' for id '1707890d-ec3c-5d2d-8e14-28826dc07c3c' has content:
      """
      {
        "telecom": {
          "email": "newlyadded@nhs.net",
          "phone_public": "01234888888",
          "phone_private": null,
          "web": "www.addemail.com"
        }
      }
      """

  Scenario: Remove website by clearing field
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 510007                  |
      | uid                 | 510007                  |
      | name                | Remove Web Practice     |
      | odscode             | B51007                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 16 Service Street       |
      | town                | SERVICETOWN             |
      | postcode            | SE1 7AA                 |
      | publicphone         | 01234 999999            |
      | email               | remove@nhs.net          |
      | web                 | www.toberemoved.com     |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Remove Web Practice     |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '510007' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510007' with version 1
    And field 'telecom' on table 'healthcare-service' for id 'd32c2b34-0af1-5d81-bead-6c282e23520a' has content:
      """
      {
        "telecom": {
          "email": "remove@nhs.net",
          "phone_public": "01234999999",
          "phone_private": null,
          "web": "www.toberemoved.com"
        }
      }
      """

    Given the "Service" with id "510007" is updated with attributes
      | key | value |
      | web |       |

    When the data migration process is run for table 'services', ID '510007' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#510007' with version 2
    And field 'telecom' on table 'healthcare-service' for id 'd32c2b34-0af1-5d81-bead-6c282e23520a' has content:
      """
      {
        "telecom": {
          "email": "remove@nhs.net",
          "phone_public": "01234999999",
          "phone_private": null,
          "web": null
        }
      }
      """
