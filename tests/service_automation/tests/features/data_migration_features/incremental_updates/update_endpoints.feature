@data-migration @incremental-update
Feature: Incremental Updates - Endpoint Changes
  Comprehensive tests for endpoint modifications during incremental updates

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  # ============================================================================
  # SINGLE ENDPOINT UPDATE SCENARIOS
  # ============================================================================

  Scenario: Update endpoint address
    Given a "Service" exists in DoS with attributes
      | key                 | value                    |
      | id                  | 570001                   |
      | uid                 | 570001                   |
      | name                | Endpoint Update Practice |
      | odscode             | G57001                   |
      | openallhours        | FALSE                    |
      | restricttoreferrals | FALSE                    |
      | address             | 1 Endpoint Street        |
      | town                | ENDPOINTTOWN             |
      | postcode            | EN1 1AA                  |
      | publicphone         | 01234 570001             |
      | email               | ep1@nhs.net              |
      | web                 | www.ep1.com              |
      | createdtime         | 2024-01-01 08:00:00.000  |
      | modifiedtime        | 2024-01-01 08:00:00.000  |
      | typeid              | 100                      |
      | statusid            | 1                        |
      | publicname          | Endpoint Update Practice |
      | latitude            | 51.5074                  |
      | longitude           | -0.1278                  |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600001                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | original@nhs.net                                            |
      | comment              | Original endpoint|
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570001                                                      |

    When the data migration process is run for table 'services', ID '570001' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570001' with version 1
    And field 'endpoints' on table 'organisation' for id '12737b36-7811-563e-82c8-c50c8c093542' has content:
      """
      {
        "endpoints": [
          {
            "id": "a94b1367-ac5b-591e-b8f1-a26bb8713f6a",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T13:57:24.828283Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T13:57:24.828283Z",
            "address": "original@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600001,
            "isCompressionEnabled": false,
            "managedByOrganisation": "12737b36-7811-563e-82c8-c50c8c093542",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Original endpoint"
          }
        ]
      }
      """

    Given the "ServiceEndpoint" with id "600001" is updated with attributes
      | key     | value           |
      | address | updated@nhs.net |

    When the data migration process is run for table 'services', ID '570001' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570001' with version 2
    And field 'endpoints' on table 'organisation' for id '12737b36-7811-563e-82c8-c50c8c093542' has content:
      """
      {
        "endpoints": [
          {
            "id": "a94b1367-ac5b-591e-b8f1-a26bb8713f6a",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T13:57:24.828283Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T13:57:24.828283Z",
            "address": "updated@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600001,
            "isCompressionEnabled": false,
            "managedByOrganisation": "12737b36-7811-563e-82c8-c50c8c093542",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Original endpoint"
          }
        ]
      }
      """

  Scenario: Update endpoint transport type
    Given a "Service" exists in DoS with attributes
      | key                 | value                     |
      | id                  | 570002                    |
      | uid                 | 570002                    |
      | name                | Transport Update Practice |
      | odscode             | G57002                    |
      | openallhours        | FALSE                     |
      | restricttoreferrals | FALSE                     |
      | address             | 2 Endpoint Street         |
      | town                | ENDPOINTTOWN              |
      | postcode            | EN1 2AA                   |
      | publicphone         | 01234 570002              |
      | email               | ep2@nhs.net               |
      | web                 | www.ep2.com               |
      | createdtime         | 2024-01-01 08:00:00.000   |
      | modifiedtime        | 2024-01-01 08:00:00.000   |
      | typeid              | 100                       |
      | statusid            | 1                         |
      | publicname          | Transport Update Practice |
      | latitude            | 51.5074                   |
      | longitude           | -0.1278                   |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600002                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | transport@nhs.net                                           |
      | comment              | Original transport                                          |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570002                                                      |

    When the data migration process is run for table 'services', ID '570002' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570002' with version 1
    And field 'endpoints' on table 'organisation' for id 'c8ea0235-6161-5255-839d-5273530ee914' has content:
      """
      {
        "endpoints": [
          {
            "id": "6f919c04-86aa-584d-87d1-15ba1a10653d",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T14:05:30.123456Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T14:05:30.123456Z",
            "address": "transport@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600002,
            "isCompressionEnabled": false,
            "managedByOrganisation": "c8ea0235-6161-5255-839d-5273530ee914",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Original transport"
          }
        ]
      }
      """

    Given the "ServiceEndpoint" with id "600002" is updated with attributes
      | key       | value                      |
      | transport | itk                        |
      | address   | https://updated-itk.nhs.uk |
      | format    | CDA                        |


    When the data migration process is run for table 'services', ID '570002' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570002' with version 2
    And field 'endpoints' on table 'organisation' for id 'c8ea0235-6161-5255-839d-5273530ee914' has content:
      """
      {
        "endpoints": [
          {
            "id": "6f919c04-86aa-584d-87d1-15ba1a10653d",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T14:05:30.123456Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T14:10:45.654321Z",
            "address": "https://updated-itk.nhs.uk",
            "connectionType": "itk",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600002,
            "isCompressionEnabled": false,
            "managedByOrganisation": "c8ea0235-6161-5255-839d-5273530ee914",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/hl7-cda+xml",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Original transport"
          }
        ]
      }
      """

  Scenario: Update endpoint compression setting
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 570003                      |
      | uid                 | 570003                      |
      | name                | Compression Update Practice |
      | odscode             | G57003                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 3 Endpoint Street           |
      | town                | ENDPOINTTOWN                |
      | postcode            | EN1 3AA                     |
      | publicphone         | 01234 570003                |
      | email               | ep3@nhs.net                 |
      | web                 | www.ep3.com                 |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Compression Update Practice |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600003                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | compress@nhs.net                                            |
      | comment              | Uncompressed originally                                     |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570003                                                      |

    When the data migration process is run for table 'services', ID '570003' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570003' with version 1
    And field 'endpoints' on table 'organisation' for id '16c77f52-4d36-54b4-ad4c-9ae55334dc0a' has content:
      """
      {
        "endpoints": [
          {
            "id": "702a49a1-6e1a-588d-9976-9577bffcc382",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T14:15:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T14:15:00.000000Z",
            "address": "compress@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600003,
            "isCompressionEnabled": false,
            "managedByOrganisation": "16c77f52-4d36-54b4-ad4c-9ae55334dc0a",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Uncompressed originally"
          }
        ]
      }
      """


    Given the "ServiceEndpoint" with id "600003" is updated with attributes
      | key                  | value      |
      | iscompressionenabled | compressed |

    When the data migration process is run for table 'services', ID '570003' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570003' with version 2
    And field 'endpoints' on table 'organisation' for id '16c77f52-4d36-54b4-ad4c-9ae55334dc0a' has content:
      """
      {
        "endpoints": [
          {
            "id": "702a49a1-6e1a-588d-9976-9577bffcc382",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T14:15:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T14:20:00.000000Z",
            "address": "compress@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600003,
            "isCompressionEnabled": true,
            "managedByOrganisation": "16c77f52-4d36-54b4-ad4c-9ae55334dc0a",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Uncompressed originally"
          }
        ]
      }
      """


  Scenario: Update endpoint order
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570004                  |
      | uid                 | 570004                  |
      | name                | Order Update Practice   |
      | odscode             | G57004                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 4 Endpoint Street       |
      | town                | ENDPOINTTOWN            |
      | postcode            | EN1 4AA                 |
      | publicphone         | 01234 570004            |
      | email               | ep4@nhs.net             |
      | web                 | www.ep4.com             |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Order Update Practice   |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600004                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | order@nhs.net                                               |
      | comment              | Order 1                                                     |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570004                                                      |

    When the data migration process is run for table 'services', ID '570004' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570004' with version 1
    And field 'endpoints' on table 'organisation' for id '951d528e-4c8b-5057-a598-823cf749659c' has content:
      """
      {
        "endpoints": [
          {
            "id": "fb3f7669-8cb6-50a5-ae55-45324c4bce9b",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T14:30:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T14:30:00.000000Z",
            "address": "order@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600004,
            "isCompressionEnabled": false,
            "managedByOrganisation": "951d528e-4c8b-5057-a598-823cf749659c",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Order 1"
          }
        ]
      }
      """

    Given the "ServiceEndpoint" with id "600004" is updated with attributes
      | key           | value |
      | endpointorder | 5     |

    When the data migration process is run for table 'services', ID '570004' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570004' with version 2
    And field 'endpoints' on table 'organisation' for id '951d528e-4c8b-5057-a598-823cf749659c' has content:
      """
      {
        "endpoints": [
          {
            "id": "fb3f7669-8cb6-50a5-ae55-45324c4bce9b",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T14:30:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T14:35:00.000000Z",
            "address": "order@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600004,
            "isCompressionEnabled": false,
            "managedByOrganisation": "951d528e-4c8b-5057-a598-823cf749659c",
            "name": null,
            "order": 5,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Order 1"
          }
        ]
      }
      """

  # ============================================================================
  # ADD NEW ENDPOINT SCENARIOS
  # ============================================================================

  Scenario: Add a new endpoint to existing service
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570010                  |
      | uid                 | 570010                  |
      | name                | Add Endpoint Practice   |
      | odscode             | G57010                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 10 Endpoint Street      |
      | town                | ENDPOINTTOWN            |
      | postcode            | EN1 0AA                 |
      | publicphone         | 01234 570010            |
      | email               | ep10@nhs.net            |
      | web                 | www.ep10.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Add Endpoint Practice   |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600010                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | original@nhs.net                                            |
      | comment              | Original endpoint                                           |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570010                                                      |

    When the data migration process is run for table 'services', ID '570010' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570010' with version 1
    And field 'endpoints' on table 'organisation' for id '294d28aa-416f-5f70-b859-abf741b34f2f' has content:
      """
      {
        "endpoints": [
          {
            "id": "7699d362-a4a3-5362-8a8b-4e3fac3f7b1c",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T15:00:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T15:00:00.000000Z",
            "address": "original@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600010,
            "isCompressionEnabled": false,
            "managedByOrganisation": "294d28aa-416f-5f70-b859-abf741b34f2f",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Original endpoint"
          }
        ]
      }
      """

    # Add a new endpoint
    Given a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                                             |
      | id                   | 600011                                                                            |
      | endpointorder        | 2                                                                                 |
      | transport            | itk                                                                               |
      | format               | CDA                                                                               |
      | interaction          | urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                                           |
      | address              | https://new-endpoint.nhs.uk                                                       |
      | comment              | Newly added endpoint                                                              |
      | iscompressionenabled | uncompressed                                                                      |
      | serviceid            | 570010                                                                            |

    When the data migration process is run for table 'services', ID '570010' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570010' with version 2
    And field 'endpoints' on table 'organisation' for id '294d28aa-416f-5f70-b859-abf741b34f2f' has content:
      """
      {
        "endpoints": [
          {
            "id": "7699d362-a4a3-5362-8a8b-4e3fac3f7b1c",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T15:00:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T15:10:00.000000Z",
            "address": "original@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600010,
            "isCompressionEnabled": false,
            "managedByOrganisation": "294d28aa-416f-5f70-b859-abf741b34f2f",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Original endpoint"
          },
          {
            "id": "c8ece154-9853-56d5-8a8a-ed96f839d753",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T15:10:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T15:10:00.000000Z",
            "address": "https://new-endpoint.nhs.uk",
            "connectionType": "itk",
            "businessScenario": "Primary",
            "identifier_oldDoS_id": 600011,
            "isCompressionEnabled": false,
            "managedByOrganisation": "294d28aa-416f-5f70-b859-abf741b34f2f",
            "name": null,
            "order": 2,
            "payloadMimeType": "application/hl7-cda+xml",
            "payloadType": "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Newly added endpoint"
          }
        ]
      }
      """

  Scenario: Add first endpoint to service without endpoints
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570011                  |
      | uid                 | 570011                  |
      | name                | No Endpoint Practice    |
      | odscode             | G57011                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 11 Endpoint Street      |
      | town                | ENDPOINTTOWN            |
      | postcode            | EN1 1BB                 |
      | publicphone         | 01234 570011            |
      | email               | ep11@nhs.net            |
      | web                 | www.ep11.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | No Endpoint Practice    |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    # Service initially has no endpoints
    When the data migration process is run for table 'services', ID '570011' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570011' with version 1
    And field 'endpoints' on table 'organisation' for id '4bb9c4e0-0aea-54e5-9701-1eda9173f399' has content:
      """
      {
        "endpoints": []
      }
      """

    # Add the first endpoint
    Given a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600012                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | first-endpoint@nhs.net                                      |
      | comment              | First endpoint added                                        |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570011                                                      |

    When the data migration process is run for table 'services', ID '570011' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570011' with version 2
    And field 'endpoints' on table 'organisation' for id '4bb9c4e0-0aea-54e5-9701-1eda9173f399' has content:
      """
      {
        "endpoints": [
          {
            "id": "9ab0e4d0-7b0b-5513-a476-494dfb763f36",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T15:30:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T15:30:00.000000Z",
            "address": "first-endpoint@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600012,
            "isCompressionEnabled": false,
            "managedByOrganisation": "4bb9c4e0-0aea-54e5-9701-1eda9173f399",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "First endpoint added"
          }
        ]
      }
      """


  Scenario: Add multiple new endpoints simultaneously
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570012                  |
      | uid                 | 570012                  |
      | name                | Multi Add Practice      |
      | odscode             | G57012                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 12 Endpoint Street      |
      | town                | ENDPOINTTOWN            |
      | postcode            | EN1 2BB                 |
      | publicphone         | 01234 570012            |
      | email               | ep12@nhs.net            |
      | web                 | www.ep12.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Multi Add Practice      |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '570012' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570012' with version 1
    And field 'endpoints' on table 'organisation' for id 'e259ae2f-0dd9-5ff0-917a-be8d3dc300f4' has content:
      """
      {
        "endpoints": []
      }
      """

    # Add three new endpoints at once
    Given a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600013                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | new1@nhs.net                                                |
      | comment              | First new endpoint                                          |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570012                                                      |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                                             |
      | id                   | 600014                                                                            |
      | endpointorder        | 2                                                                                 |
      | transport            | itk                                                                               |
      | format               | CDA                                                                               |
      | interaction          | urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                                           |
      | address              | https://new2.nhs.uk                                                               |
      | comment              | Second new endpoint                                                               |
      | iscompressionenabled | compressed                                                                        |
      | serviceid            | 570012                                                                            |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                                   |
      | id                   | 600015                                                                  |
      | endpointorder        | 3                                                                       |
      | transport            | itk                                                                     |
      | format               | CDA                                                                     |
      | interaction          | urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                                 |
      | address              | https://new3.nhs.uk                                                     |
      | comment              | Third new                                                               |
      | iscompressionenabled | uncompressed                                                            |
      | serviceid            | 570012                                                                  |

    When the data migration process is run for table 'services', ID '570012' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570012' with version 2
    And field 'endpoints' on table 'organisation' for id 'e259ae2f-0dd9-5ff0-917a-be8d3dc300f4' has content:
      """
      {
        "endpoints": [
          {
            "id": "10409a5d-9727-5f7c-a478-15b74902b398",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T16:00:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T16:00:00.000000Z",
            "address": "new1@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600013,
            "isCompressionEnabled": false,
            "managedByOrganisation": "e259ae2f-0dd9-5ff0-917a-be8d3dc300f4",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "First new endpoint"
          },
          {
            "id": "86735dd5-552b-5186-8405-0b9840c1ee1e",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T16:00:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T16:00:00.000000Z",
            "address": "https://new2.nhs.uk",
            "connectionType": "itk",
            "businessScenario": "Primary",
            "identifier_oldDoS_id": 600014,
            "isCompressionEnabled": true,
            "managedByOrganisation": "e259ae2f-0dd9-5ff0-917a-be8d3dc300f4",
            "name": null,
            "order": 2,
            "payloadMimeType": "application/hl7-cda+xml",
            "payloadType": "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Second new endpoint"
          },
          {
            "id": "fd557a29-d6f8-5cdb-be1a-1c64d594b080",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T16:00:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T16:00:00.000000Z",
            "address": "https://new3.nhs.uk",
            "connectionType": "itk",
            "businessScenario": "Primary",
            "identifier_oldDoS_id": 600015,
            "isCompressionEnabled": false,
            "managedByOrganisation": "e259ae2f-0dd9-5ff0-917a-be8d3dc300f4",
            "name": null,
            "order": 3,
            "payloadMimeType": "application/hl7-cda+xml",
            "payloadType": "urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Third new"
          }
        ]
      }
      """

  # ============================================================================
  # REMOVE ENDPOINT SCENARIOS
  # ============================================================================

  Scenario: Remove an endpoint from service with multiple endpoints
    Given a "Service" exists in DoS with attributes
      | key                 | value                    |
      | id                  | 570020                   |
      | uid                 | 570020                   |
      | name                | Remove Endpoint Practice |
      | odscode             | G57020                   |
      | openallhours        | FALSE                    |
      | restricttoreferrals | FALSE                    |
      | address             | 20 Endpoint Street       |
      | town                | ENDPOINTTOWN             |
      | postcode            | EN2 0AA                  |
      | publicphone         | 01234 570020             |
      | email               | ep20@nhs.net             |
      | web                 | www.ep20.com             |
      | createdtime         | 2024-01-01 08:00:00.000  |
      | modifiedtime        | 2024-01-01 08:00:00.000  |
      | typeid              | 100                      |
      | statusid            | 1                        |
      | publicname          | Remove Endpoint Practice |
      | latitude            | 51.5074                  |
      | longitude           | -0.1278                  |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600020                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | keep@nhs.net                                                |
      | comment              | This one stays                                              |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570020                                                      |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                                             |
      | id                   | 600021                                                                            |
      | endpointorder        | 2                                                                                 |
      | transport            | itk                                                                               |
      | format               | CDA                                                                               |
      | interaction          | urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                                           |
      | address              | https://remove-me.nhs.uk                                                          |
      | comment              | This one will be removed                                                          |
      | iscompressionenabled | uncompressed                                                                      |
      | serviceid            | 570020                                                                            |

    When the data migration process is run for table 'services', ID '570020' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570020' with version 1
    And field 'endpoints' on table 'organisation' for id '05db0532-0f98-580e-8c15-8cffe158934e' has content:
      """
      {
        "endpoints": [
          {
            "id": "cf1d30d0-e07d-5b5d-af57-31aa8057fb57",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T16:30:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T16:30:00.000000Z",
            "address": "keep@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600020,
            "isCompressionEnabled": false,
            "managedByOrganisation": "05db0532-0f98-580e-8c15-8cffe158934e",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "This one stays"
          },
          {
            "id": "d38262b1-c82e-5972-a89d-508ab58d2ffc",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T16:30:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T16:30:00.000000Z",
            "address": "https://remove-me.nhs.uk",
            "connectionType": "itk",
            "businessScenario": "Primary",
            "identifier_oldDoS_id": 600021,
            "isCompressionEnabled": false,
            "managedByOrganisation": "05db0532-0f98-580e-8c15-8cffe158934e",
            "name": null,
            "order": 2,
            "payloadMimeType": "application/hl7-cda+xml",
            "payloadType": "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "This one will be removed"
          }
        ]
      }
      """

    # Remove one endpoint
    Given the "ServiceEndpoint" with id "600021" is deleted from DoS

    When the data migration process is run for table 'services', ID '570020' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570020' with version 2
    And field 'endpoints' on table 'organisation' for id '05db0532-0f98-580e-8c15-8cffe158934e' has content:
      """
      {
        "endpoints": [
          {
            "id": "cf1d30d0-e07d-5b5d-af57-31aa8057fb57",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T16:30:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T16:35:00.000000Z",
            "address": "keep@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600020,
            "isCompressionEnabled": false,
            "managedByOrganisation": "05db0532-0f98-580e-8c15-8cffe158934e",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "This one stays"
          }
        ]
      }
      """

  Scenario: Remove all endpoints from a service
    Given a "Service" exists in DoS with attributes
      | key                 | value                         |
      | id                  | 570021                        |
      | uid                 | 570021                        |
      | name                | Remove All Endpoints Practice |
      | odscode             | G57021                        |
      | openallhours        | FALSE                         |
      | restricttoreferrals | FALSE                         |
      | address             | 21 Endpoint Street            |
      | town                | ENDPOINTTOWN                  |
      | postcode            | EN2 1AA                       |
      | publicphone         | 01234 570021                  |
      | email               | ep21@nhs.net                  |
      | web                 | www.ep21.com                  |
      | createdtime         | 2024-01-01 08:00:00.000       |
      | modifiedtime        | 2024-01-01 08:00:00.000       |
      | typeid              | 100                           |
      | statusid            | 1                             |
      | publicname          | Remove All Endpoints Practice |
      | latitude            | 51.5074                       |
      | longitude           | -0.1278                       |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600022                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | remove1@nhs.net                                             |
      | comment              | Will be removed                                             |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570021                                                      |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600023                                                      |
      | endpointorder        | 2                                                           |
      | transport            | itk                                                         |
      | format               | CDA                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                     |
      | address              | https://remove2.nhs.uk                                      |
      | comment              | Also removed                                                |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570021                                                      |

    When the data migration process is run for table 'services', ID '570021' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570021' with version 1

    # Remove all endpoints
    Given the "ServiceEndpoint" with id "600022" is deleted from DoS
    And the "ServiceEndpoint" with id "600023" is deleted from DoS

    When the data migration process is run for table 'services', ID '570021' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570021' with version 2
    And field 'endpoints' on table 'organisation' for id '8ecc24b9-6ccd-5205-a35d-768c8f7d934b' has content:
      """
      {
        "endpoints": []
      }
      """

  # ============================================================================
  # COMBINATION SCENARIOS (ADD, UPDATE, REMOVE)
  # ============================================================================

  Scenario: Update one endpoint while adding another
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570030                  |
      | uid                 | 570030                  |
      | name                | Update And Add Practice |
      | odscode             | G57030                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 30 Endpoint Street      |
      | town                | ENDPOINTTOWN            |
      | postcode            | EN3 0AA                 |
      | publicphone         | 01234 570030            |
      | email               | ep30@nhs.net            |
      | web                 | www.ep30.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Update And Add Practice |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600030                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | original@nhs.net                                            |
      | comment              | Original endpoint                                           |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570030                                                      |

    When the data migration process is run for table 'services', ID '570030' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570030' with version 1
    And field 'endpoints' on table 'organisation' for id '067095c1-703d-50b6-aae4-fcf724c1ced5' has content:
      """
      {
        "endpoints": [
          {
            "id": "407a3abf-3114-57ca-b41e-557d716087e8",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T17:00:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T17:00:00.000000Z",
            "address": "original@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600030,
            "isCompressionEnabled": false,
            "managedByOrganisation": "067095c1-703d-50b6-aae4-fcf724c1ced5",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Original endpoint"
          }
        ]
      }
      """

    # Update existing endpoint AND add a new one
    Given the "ServiceEndpoint" with id "600030" is updated with attributes
      | key     | value           |
      | address | updated@nhs.net |
      | comment | Updated address |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600031                                                      |
      | endpointorder        | 2                                                           |
      | transport            | itk                                                         |
      | format               | CDA                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                     |
      | address              | https://new-endpoint.nhs.uk                                 |
      | comment              | Brand new endpoint                                          |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570030                                                      |

    When the data migration process is run for table 'services', ID '570030' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570030' with version 2
    And field 'endpoints' on table 'organisation' for id '067095c1-703d-50b6-aae4-fcf724c1ced5' has content:
      """
      {
        "endpoints": [
          {
            "id": "407a3abf-3114-57ca-b41e-557d716087e8",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T17:00:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T17:05:00.000000Z",
            "address": "updated@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600030,
            "isCompressionEnabled": false,
            "managedByOrganisation": "067095c1-703d-50b6-aae4-fcf724c1ced5",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Updated address"
          },
          {
            "id": "6a33c9f8-2a81-517b-b06f-8a2872bccf23",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T17:05:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T17:05:00.000000Z",
            "address": "https://new-endpoint.nhs.uk",
            "connectionType": "itk",
            "businessScenario": "Primary",
            "identifier_oldDoS_id": 600031,
            "isCompressionEnabled": false,
            "managedByOrganisation": "067095c1-703d-50b6-aae4-fcf724c1ced5",
            "name": null,
            "order": 2,
            "payloadMimeType": "application/hl7-cda+xml",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Brand new endpoint"
          }
        ]
      }
      """

  Scenario: Remove one endpoint while adding another
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570031                  |
      | uid                 | 570031                  |
      | name                | Remove And Add Practice |
      | odscode             | G57031                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 31 Endpoint Street      |
      | town                | ENDPOINTTOWN            |
      | postcode            | EN3 1AA                 |
      | publicphone         | 01234 570031            |
      | email               | ep31@nhs.net            |
      | web                 | www.ep31.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Remove And Add Practice |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600032                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | to-be-removed@nhs.net                                       |
      | comment              | Will be removed                                             |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570031                                                      |

    When the data migration process is run for table 'services', ID '570031' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570031' with version 1
    And field 'endpoints' on table 'organisation' for id 'c9cd8718-e05d-5fa3-8b62-1190ee26e828' has content:
      """
      {
        "endpoints": [
          {
            "id": "4996f42b-1d31-5c1b-89e5-eecf38730ad6",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T17:30:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T17:30:00.000000Z",
            "address": "to-be-removed@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600032,
            "isCompressionEnabled": false,
            "managedByOrganisation": "c9cd8718-e05d-5fa3-8b62-1190ee26e828",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Will be removed"
          }
        ]
      }
      """


    # Remove the old endpoint and add a new one
    Given the "ServiceEndpoint" with id "600032" is deleted from DoS

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600033                                                      |
      | endpointorder        | 1                                                           |
      | transport            | itk                                                         |
      | format               | CDA                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                     |
      | address              | https://replacement.nhs.uk                                  |
      | comment              | Replacement endpoint                                        |
      | iscompressionenabled | compressed                                                  |
      | serviceid            | 570031                                                      |

    When the data migration process is run for table 'services', ID '570031' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570031' with version 2
    And field 'endpoints' on table 'organisation' for id 'c9cd8718-e05d-5fa3-8b62-1190ee26e828' has content:
      """
      {
        "endpoints": [
          {
            "id": "c2834526-84d3-57b0-968f-31ec9b5ad616",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T17:35:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T17:35:00.000000Z",
            "address": "https://replacement.nhs.uk",
            "connectionType": "itk",
            "businessScenario": "Primary",
            "identifier_oldDoS_id": 600033,
            "isCompressionEnabled": true,
            "managedByOrganisation": "c9cd8718-e05d-5fa3-8b62-1190ee26e828",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/hl7-cda+xml",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Replacement endpoint"
          }
        ]
      }
      """

  Scenario: Update one endpoint while removing another
    Given a "Service" exists in DoS with attributes
      | key                 | value                      |
      | id                  | 570032                     |
      | uid                 | 570032                     |
      | name                | Update And Remove Practice |
      | odscode             | G57032                     |
      | openallhours        | FALSE                      |
      | restricttoreferrals | FALSE                      |
      | address             | 32 Endpoint Street         |
      | town                | ENDPOINTTOWN               |
      | postcode            | EN3 2AA                    |
      | publicphone         | 01234 570032               |
      | email               | ep32@nhs.net               |
      | web                 | www.ep32.com               |
      | createdtime         | 2024-01-01 08:00:00.000    |
      | modifiedtime        | 2024-01-01 08:00:00.000    |
      | typeid              | 100                        |
      | statusid            | 1                          |
      | publicname          | Update And Remove Practice |
      | latitude            | 51.5074                    |
      | longitude           | -0.1278                    |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600034                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | update-me@nhs.net                                           |
      | comment              | Will be updated                                             |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570032                                                      |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600035                                                      |
      | endpointorder        | 2                                                           |
      | transport            | itk                                                         |
      | format               | CDA                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                     |
      | address              | https://remove-me.nhs.uk                                    |
      | comment              | Will be removed                                             |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570032                                                      |

    When the data migration process is run for table 'services', ID '570032' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570032' with version 1
    And field 'endpoints' on table 'organisation' for id '332cd68b-9ab7-575b-a5de-4211b30a8c67' has content:
      """
      {
        "endpoints": [
          {
            "id": "e2772556-80ed-50ca-be43-8a62cfbd4390",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T18:00:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T18:00:00.000000Z",
            "address": "update-me@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600034,
            "isCompressionEnabled": false,
            "managedByOrganisation": "332cd68b-9ab7-575b-a5de-4211b30a8c67",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Will be updated"
          },
          {
            "id": "31e3e8da-272b-5dad-bb71-154a7119b394",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T18:00:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T18:00:00.000000Z",
            "address": "https://remove-me.nhs.uk",
            "connectionType": "itk",
            "businessScenario": "Primary",
            "identifier_oldDoS_id": 600035,
            "isCompressionEnabled": false,
            "managedByOrganisation": "332cd68b-9ab7-575b-a5de-4211b30a8c67",
            "name": null,
            "order": 2,
            "payloadMimeType": "application/hl7-cda+xml",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Will be removed"
          }
        ]
      }
      """

    # Update one and remove the other
    Given the "ServiceEndpoint" with id "600034" is updated with attributes
      | key     | value                   |
      | address | updated-address@nhs.net |
      | comment | Address updated         |

    And the "ServiceEndpoint" with id "600035" is deleted from DoS

    When the data migration process is run for table 'services', ID '570032' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570032' with version 2
    And field 'endpoints' on table 'organisation' for id '332cd68b-9ab7-575b-a5de-4211b30a8c67' has content:
      """
      {
        "endpoints": [
          {
            "id": "e2772556-80ed-50ca-be43-8a62cfbd4390",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T18:00:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T18:05:00.000000Z",
            "address": "updated-address@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600034,
            "isCompressionEnabled": false,
            "managedByOrganisation": "332cd68b-9ab7-575b-a5de-4211b30a8c67",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Address updated"
          }
        ]
      }
      """

  Scenario: Add, update and remove endpoints simultaneously
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570033                  |
      | uid                 | 570033                  |
      | name                | All Ops Practice        |
      | odscode             | G57033                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 33 Endpoint Street      |
      | town                | ENDPOINTTOWN            |
      | postcode            | EN3 3AA                 |
      | publicphone         | 01234 570033            |
      | email               | ep33@nhs.net            |
      | web                 | www.ep33.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | All Ops Practice        |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600036                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | update-me@nhs.net                                           |
      | comment              | Will be updated                                             |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570033                                                      |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600037                                                      |
      | endpointorder        | 2                                                           |
      | transport            | itk                                                         |
      | format               | CDA                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                     |
      | address              | https://remove-me.nhs.uk                                    |
      | comment              | Will be removed                                             |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570033                                                      |

    When the data migration process is run for table 'services', ID '570033' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570033' with version 1
    And field 'endpoints' on table 'organisation' for id '54403489-6a03-5fcb-9197-e5fcca1ad41a' has content:
      """
      {
        "endpoints": [
          {
            "id": "4df92432-9bb7-54b6-8499-589e2e3d4cd4",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T18:30:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T18:30:00.000000Z",
            "address": "update-me@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600036,
            "isCompressionEnabled": false,
            "managedByOrganisation": "54403489-6a03-5fcb-9197-e5fcca1ad41a",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Will be updated"
          },
          {
            "id": "bb9dc471-2884-57b3-8975-a61e109ac8f6",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T18:30:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T18:30:00.000000Z",
            "address": "https://remove-me.nhs.uk",
            "connectionType": "itk",
            "businessScenario": "Primary",
            "identifier_oldDoS_id": 600037,
            "isCompressionEnabled": false,
            "managedByOrganisation": "54403489-6a03-5fcb-9197-e5fcca1ad41a",
            "name": null,
            "order": 2,
            "payloadMimeType": "application/hl7-cda+xml",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Will be removed"
          }
        ]
      }
      """

    # All three operations: add, update, and remove
    Given the "ServiceEndpoint" with id "600036" is updated with attributes
      | key                  | value           |
      | address              | updated@nhs.net |
      | iscompressionenabled | compressed      |

    And the "ServiceEndpoint" with id "600037" is deleted from DoS

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                                             |
      | id                   | 600038                                                                            |
      | endpointorder        | 3                                                                                 |
      | transport            | itk                                                                               |
      | format               | CDA                                                                               |
      | interaction          | urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                                           |
      | address              | https://new-endpoint.nhs.uk                                                       |
      | comment              | Brand new endpoint                                                                |
      | iscompressionenabled | uncompressed                                                                      |
      | serviceid            | 570033                                                                            |

    When the data migration process is run for table 'services', ID '570033' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570033' with version 2
    And field 'endpoints' on table 'organisation' for id '54403489-6a03-5fcb-9197-e5fcca1ad41a' has content:
      """
      {
        "endpoints": [
          {
            "id": "4df92432-9bb7-54b6-8499-589e2e3d4cd4",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T18:30:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T18:35:00.000000Z",
            "address": "updated@nhs.net",
            "connectionType": "email",
            "businessScenario": "Copy",
            "identifier_oldDoS_id": 600036,
            "isCompressionEnabled": true,
            "managedByOrganisation": "54403489-6a03-5fcb-9197-e5fcca1ad41a",
            "name": null,
            "order": 1,
            "payloadMimeType": "application/pdf",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Will be updated"
          },
          {
            "id": "b9416800-4b19-5278-8ffa-d0fcea7db864",
            "createdBy": "DATA_MIGRATION",
            "createdDateTime": "2026-01-12T18:35:00.000000Z",
            "modifiedBy": "DATA_MIGRATION",
            "modifiedDateTime": "2026-01-12T18:35:00.000000Z",
            "address": "https://new-endpoint.nhs.uk",
            "connectionType": "itk",
            "businessScenario": "Primary",
            "identifier_oldDoS_id": 600038,
            "isCompressionEnabled": false,
            "managedByOrganisation": "54403489-6a03-5fcb-9197-e5fcca1ad41a",
            "name": null,
            "order": 3,
            "payloadMimeType": "application/hl7-cda+xml",
            "payloadType": "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
            "service": null,
            "status": "active",
            "comment": "Brand new endpoint"
          }
        ]
      }
      """

  # ============================================================================
  # ENDPOINT NO CHANGE SCENARIOS
  # ============================================================================

  Scenario: No endpoint changes results in no update when only service timestamp changes
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570040                  |
      | uid                 | 570040                  |
      | name                | No Change Practice      |
      | odscode             | G57040                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 40 Endpoint Street      |
      | town                | ENDPOINTTOWN            |
      | postcode            | EN4 0AA                 |
      | publicphone         | 01234 570040            |
      | email               | ep40@nhs.net            |
      | web                 | www.ep40.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | No Change Practice      |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600040                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | unchanged@nhs.net                                           |
      | comment              | Stays the same                                              |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570040                                                      |

    When the data migration process is run for table 'services', ID '570040' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570040' with version 1

    # Only update timestamp, no actual data changes
    Given the "Service" with id "570040" is updated with attributes
      | key          | value               |
      | modifiedtime | 2024-06-01 10:00:00 |

    When the data migration process is run for table 'services', ID '570040' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570040' with version 1

  # ============================================================================
  # MULTIPLE CONSECUTIVE UPDATE SCENARIOS
  # ============================================================================

  Scenario: Multiple consecutive endpoint updates increment version
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570050                  |
      | uid                 | 570050                  |
      | name                | Multi Update Practice   |
      | odscode             | G57050                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 50 Endpoint Street      |
      | town                | ENDPOINTTOWN            |
      | postcode            | EN5 0AA                 |
      | publicphone         | 01234 570050            |
      | email               | ep50@nhs.net            |
      | web                 | www.ep50.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Multi Update Practice   |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600050                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | version1@nhs.net                                            |
      | comment              | Version 1                                                   |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570050                                                      |

    # Initial insert - version 1
    When the data migration process is run for table 'services', ID '570050' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570050' with version 1

    # First update - version 2
    Given the "ServiceEndpoint" with id "600050" is updated with attributes
      | key     | value            |
      | address | version2@nhs.net |
      | comment | Version 2        |

    When the data migration process is run for table 'services', ID '570050' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570050' with version 2

    # Second update - version 3
    Given the "ServiceEndpoint" with id "600050" is updated with attributes
      | key     | value            |
      | address | version3@nhs.net |
      | comment | Version 3        |

    When the data migration process is run for table 'services', ID '570050' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570050' with version 3

    # Third update - add new endpoint - version 4
    Given a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600051                                                      |
      | endpointorder        | 2                                                           |
      | transport            | itk                                                         |
      | format               | CDA                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                     |
      | address              | https://version4.nhs.uk                                     |
      | comment              | Added in version 4                                          |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 570050                                                      |

    When the data migration process is run for table 'services', ID '570050' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570050' with version 4
