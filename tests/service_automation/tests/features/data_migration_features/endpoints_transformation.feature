@data-migration
Feature: Data Migration for endpoints

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Endpoints are migrated
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  | 10205752                                                    |
      | uid                                 | 138179                                                      |
      | name                                | Abbey Medical Practice, Evesham, Worcestershire             |
      | odscode                             | M81094                                                      |
      | openallhours                        | FALSE                                                       |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 5752            |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 5752 |
      | restricttoreferrals                 | TRUE                                                        |
      | address                             | Evesham Medical Centre$Abbey Lane$Evesham                   |
      | town                                | EVESHAM                                                     |
      | postcode                            | WR11 4BS                                                    |
      | easting                             | 403453                                                      |
      | northing                            | 243634                                                      |
      | publicphone                         | 01386 761111                                                |
      | nonpublicphone                      | 99999 000000                                                |
      | fax                                 | 77777 000000                                                |
      | email                               |                                                             |
      | web                                 | www.abbeymedical.com                                        |
      | createdby                           | HUMAN                                                       |
      | createdtime                         | 2011-06-29 08:00:51.000                                     |
      | modifiedby                          | HUMAN                                                       |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                     |
      | lasttemplatename                    | Midlands template R46 Append PC                             |
      | lasttemplateid                      | 244764                                                      |
      | typeid                              | 100                                                         |
      | parentid                            | 150013                                                      |
      | subregionid                         | 150013                                                      |
      | statusid                            | 1                                                           |
      | organisationid                      |                                                             |
      | returnifopenminutes                 |                                                             |
      | publicname                          | Abbey Medical Practice                                      |
      | latitude                            | 52.0910543                                                  |
      | longitude                           | -1.951003                                                   |
      | professionalreferralinfo            | Nope                                                        |
      | lastverified                        |                                                             |
      | nextverificationdue                 |                                                             |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       | reason          |
      | id                   | 500001                                                      |                 |
      | endpointorder        | 1                                                           |                 |
      | transport            | email                                                       |                 |
      | format               | PDF                                                         | test format     |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |                 |
      | businessscenario     | Copy                                                        |                 |
      | address              | dummy-endpoint-email@nhs.net                                |                 |
      | comment              | PEM SENT                                                    |                 |
      | iscompressionenabled | compressed                                                  | test compressed |
      | serviceid            | 10205752                                                    |                 |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                                                                | reason                     |
      | id                   | 500002                                                                                               |                            |
      | endpointorder        | 2                                                                                                    |                            |
      | transport            | email                                                                                                |                            |
      | format               | PDF                                                                                                  | test format                |
      | interaction          | urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0                    |                            |
      | businessscenario     | Primary                                                                                              | different businessscenario |
      | address              | dummy-endpoint-email@nhs.net                                                                         |                            |
      | comment              | ITK failed - Please advise the caller to contact the practice, reiterating the recommended timeframe |                            |
      | iscompressionenabled | uncompressed                                                                                         |                            |
      | serviceid            | 10205752                                                                                             |                            |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       | reason      |
      | id                   | 500003                                                      |             |
      | endpointorder        | 1                                                           |             |
      | transport            | itk                                                         |             |
      | format               | CDA                                                         | test format |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |             |
      | businessscenario     | Copy                                                        |             |
      | address              | https://dummy-itk-endpoint.nhs.uk                           |             |
      | comment              | PEM SENT                                                    |             |
      | iscompressionenabled | uncompressed                                                |             |
      | serviceid            | 10205752                                                    |             |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value        | reason             |
      | id                   | 500004       |                    |
      | endpointorder        | 3            |                    |
      | transport            | http         |                    |
      | format               | FHIR         | test format        |
      | interaction          | scheduling   |                    |
      | businessscenario     | Primary      |                    |
      | address              | ODS:C84016   |                    |
      | comment              |              | test empty comment |
      | iscompressionenabled | uncompressed |                    |
      | serviceid            | 10205752     |                    |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                         | reason                               |
      | id                   | 500005                                                        |                                      |
      | endpointorder        | 4                                                             |                                      |
      | transport            | telno                                                         | for transport telno                  |
      | format               | HTML                                                          | payloadMimeType should be left blank |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0   |                                      |
      | businessscenario     | Primary                                                       |                                      |
      | address              | telephone number                                              |                                      |
      | comment              | If email fails, please telephone the practice on 12345 123456 |                                      |
      | iscompressionenabled | uncompressed                                                  |                                      |
      | serviceid            | 10205752                                                      |                                      |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value        | reason                                 |
      | id                   | 500006       |                                        |
      | endpointorder        | 1            |                                        |
      | transport            | telno        | transport telno                        |
      | format               |              | confirm we can handle null format      |
      | interaction          |              | confirm we can handle null interaction |
      | businessscenario     | Primary      |                                        |
      | address              | 12345123456  |                                        |
      | comment              |              |                                        |
      | iscompressionenabled | uncompressed |                                        |
      | serviceid            | 10205752     |                                        |

    When the data migration process is run for table 'services', ID '10205752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then field 'endpoints' on table 'organisation' for id 'd7976aa8-2da8-5da2-9426-f6f42d0565f2' has content:
      """
      {
          "endpoints": [
              {
                  "address": "dummy-endpoint-email@nhs.net",
                  "connectionType": "email",
                  "createdBy": "DATA_MIGRATION",
                  "createdDateTime": "2025-11-28T12:49:13.248485Z",
                  "description": "Copy",
                  "id": "d428a4f3-ed5f-5c8c-b3a8-9e4b266d05c0",
                  "identifier_oldDoS_id": 500001,
                  "isCompressionEnabled": true,
                  "managedByOrganisation": "d7976aa8-2da8-5da2-9426-f6f42d0565f2",
                  "modifiedBy": "DATA_MIGRATION",
                  "modifiedDateTime": "2025-11-28T12:49:13.248485Z",
                  "name": null,
                  "order": 1,
                  "payloadMimeType": "application/pdf",
                  "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
                  "service": null,
                  "status": "active",
                  "comment": "PEM SENT"
              },
              {
                  "address": "dummy-endpoint-email@nhs.net",
                  "connectionType": "email",
                  "createdBy": "DATA_MIGRATION",
                  "createdDateTime": "2025-11-28T12:49:13.248485Z",
                  "description": "Primary",
                  "id": "012dc0d6-f1c1-544f-a83c-ba2b964e428e",
                  "identifier_oldDoS_id": 500002,
                  "isCompressionEnabled": false,
                  "managedByOrganisation": "d7976aa8-2da8-5da2-9426-f6f42d0565f2",
                  "modifiedBy": "DATA_MIGRATION",
                  "modifiedDateTime": "2025-11-28T12:49:13.248485Z",
                  "name": null,
                  "order": 2,
                  "payloadMimeType": "application/pdf",
                  "payloadType": "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
                  "service": null,
                  "status": "active",
                  "comment": "ITK failed - Please advise the caller to contact the practice, reiterating the recommended timeframe"
              },
              {
                  "address": "https://dummy-itk-endpoint.nhs.uk",
                  "connectionType": "itk",
                  "createdBy": "DATA_MIGRATION",
                  "createdDateTime": "2025-11-28T12:49:13.248485Z",
                  "description": "Copy",
                  "id": "82ddb087-8a00-50eb-8b68-2d1baacf52de",
                  "identifier_oldDoS_id": 500003,
                  "isCompressionEnabled": false,
                  "managedByOrganisation": "d7976aa8-2da8-5da2-9426-f6f42d0565f2",
                  "modifiedBy": "DATA_MIGRATION",
                  "modifiedDateTime": "2025-11-28T12:49:13.248485Z",
                  "name": null,
                  "order": 1,
                  "payloadMimeType": "application/hl7-cda+xml",
                  "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
                  "service": null,
                  "status": "active",
                  "comment": "PEM SENT"
              },
              {
                  "address": "ODS:C84016",
                  "connectionType": "http",
                  "createdBy": "DATA_MIGRATION",
                  "createdDateTime": "2025-11-28T12:49:13.248485Z",
                  "description": "Primary",
                  "id": "bab8991d-a550-599c-a6b1-724963efac89",
                  "identifier_oldDoS_id": 500004,
                  "isCompressionEnabled": false,
                  "managedByOrganisation": "d7976aa8-2da8-5da2-9426-f6f42d0565f2",
                  "modifiedBy": "DATA_MIGRATION",
                  "modifiedDateTime": "2025-11-28T12:49:13.248485Z",
                  "name": null,
                  "order": 3,
                  "payloadMimeType": "application/fhir",
                  "payloadType": "scheduling",
                  "service": null,
                  "status": "active",
                  "comment": null
              },
              {
                  "address": "telephone number",
                  "connectionType": "telno",
                  "createdBy": "DATA_MIGRATION",
                  "createdDateTime": "2025-11-28T12:49:13.248485Z",
                  "description": "Primary",
                  "id": "abdbab5b-da78-5f26-9974-65db28fbe714",
                  "identifier_oldDoS_id": 500005,
                  "isCompressionEnabled": false,
                  "managedByOrganisation": "d7976aa8-2da8-5da2-9426-f6f42d0565f2",
                  "modifiedBy": "DATA_MIGRATION",
                  "modifiedDateTime": "2025-11-28T12:49:13.248485Z",
                  "name": null,
                  "order": 4,
                  "payloadMimeType": null,
                  "payloadType": null,
                  "service": null,
                  "status": "active",
                  "comment": "If email fails, please telephone the practice on 12345 123456"
              },
              {
                  "address": "12345123456",
                  "connectionType": "telno",
                  "createdBy": "DATA_MIGRATION",
                  "createdDateTime": "2025-11-28T12:49:13.248485Z",
                  "description": "Primary",
                  "id": "57db7d5d-f9a4-58fb-828c-47cbe3e7e3d5",
                  "identifier_oldDoS_id": 500006,
                  "isCompressionEnabled": false,
                  "managedByOrganisation": "d7976aa8-2da8-5da2-9426-f6f42d0565f2",
                  "modifiedBy": "DATA_MIGRATION",
                  "modifiedDateTime": "2025-11-28T12:49:13.248485Z",
                  "name": null,
                  "order": 1,
                  "payloadMimeType": null,
                  "payloadType": null,
                  "service": null,
                  "status": "active",
                  "comment": null
              }
          ]
      }
      """


  Scenario: Endpoints are migrated for an empty service
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  | 10305752                                                    |
      | uid                                 | 138179                                                      |
      | name                                | Abbey Medical Practice, Evesham, Worcestershire             |
      | odscode                             | M81094                                                      |
      | openallhours                        | FALSE                                                       |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 5752            |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 5752 |
      | restricttoreferrals                 | TRUE                                                        |
      | address                             | Evesham Medical Centre$Abbey Lane$Evesham                   |
      | town                                | EVESHAM                                                     |
      | postcode                            | WR11 4BS                                                    |
      | easting                             | 403453                                                      |
      | northing                            | 243634                                                      |
      | publicphone                         | 01386 761111                                                |
      | nonpublicphone                      | 99999 000000                                                |
      | fax                                 | 77777 000000                                                |
      | email                               |                                                             |
      | web                                 | www.abbeymedical.com                                        |
      | createdby                           | HUMAN                                                       |
      | createdtime                         | 2011-06-29 08:00:51.000                                     |
      | modifiedby                          | HUMAN                                                       |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                     |
      | lasttemplatename                    | Midlands template R46 Append PC                             |
      | lasttemplateid                      | 244764                                                      |
      | typeid                              | 100                                                         |
      | parentid                            | 150013                                                      |
      | subregionid                         | 150013                                                      |
      | statusid                            | 1                                                           |
      | organisationid                      |                                                             |
      | returnifopenminutes                 |                                                             |
      | publicname                          | Abbey Medical Practice                                      |
      | latitude                            | 52.0910543                                                  |
      | longitude                           | -1.951003                                                   |
      | professionalreferralinfo            | Nope                                                        |
      | lastverified                        |                                                             |
      | nextverificationdue                 |                                                             |
    And a "ServiceEndpoint" exists in DoS with attributes
      | key           | value    | reason |
      | id            | 500001   |        |
      | endpointorder | 1        |        |
      | serviceid     | 10305752 |        |
    When the data migration process is run for table 'services', ID '10305752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 0 transformed, 0 migrated, 0 skipped and 1 errors
    Then error log containing message: '3 validation errors for Endpoint' was found
    Then there is 0 organisation, 0 location and 0 healthcare services created

  Scenario: Comment field is migrated for endpoints
    Given a "Service" exists in DoS with attributes
      | key                    | value                          |
      | id                     | 10405752                       |
      | uid                    | 138180                         |
      | name                   | Test Service for Comment Field |
      | odscode                | M81095                         |
      | openallhours           | FALSE                          |
      | restricttoreferrals    | FALSE                          |
      | address                | Test Address$Test Street       |
      | town                   | TestTown                       |
      | postcode               | TE1 1ST                        |
      | publicname             | Test Service Comment           |
      | typeid                 | 100                            |
      | statusid               | 1                              |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600001                                                      |
      | endpointorder        | 1                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | test-endpoint@nhs.net                                       |
      | comment              | This is a test comment for FTRS-2011                        |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 10405752                                                    |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                                             |
      | id                   | 600002                                                                            |
      | endpointorder        | 2                                                                                 |
      | transport            | itk                                                                               |
      | format               | CDA                                                                               |
      | interaction          | urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                                           |
      | address              | https://test-endpoint.nhs.uk                                                      |
      | comment              |                                                                                   |
      | iscompressionenabled | uncompressed                                                                      |
      | serviceid            | 10405752                                                                          |

    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                       |
      | id                   | 600003                                                      |
      | endpointorder        | 3                                                           |
      | transport            | email                                                       |
      | format               | PDF                                                         |
      | interaction          | urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Copy                                                        |
      | address              | another-test@nhs.net                                        |
      | iscompressionenabled | uncompressed                                                |
      | serviceid            | 10405752                                                    |

    When the data migration process is run for table 'services', ID '10405752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then field 'endpoints' on table 'organisation' for id '98af3729-aed2-57e5-b65e-d569aa70784e' has content:
      """
      {
          "endpoints": [
              {
                  "id": "a94b1367-ac5b-591e-b8f1-a26bb8713f6a",
                  "identifier_oldDoS_id": 600001,
                  "status": "active",
                  "connectionType": "email",
                  "name": null,
                  "payloadMimeType": "application/pdf",
                  "description": "Copy",
                  "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
                  "address": "test-endpoint@nhs.net",
                  "managedByOrganisation": "98af3729-aed2-57e5-b65e-d569aa70784e",
                  "service": null,
                  "order": 1,
                  "isCompressionEnabled": false,
                  "createdBy": "DATA_MIGRATION",
                  "modifiedBy": "DATA_MIGRATION",
                  "comment": "This is a test comment for FTRS-2011"
              },
              {
                  "id": "6f919c04-86aa-584d-87d1-15ba1a10653d",
                  "identifier_oldDoS_id": 600002,
                  "status": "active",
                  "connectionType": "itk",
                  "name": null,
                  "payloadMimeType": "application/hl7-cda+xml",
                  "description": "Primary",
                  "payloadType": "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
                  "address": "https://test-endpoint.nhs.uk",
                  "managedByOrganisation": "98af3729-aed2-57e5-b65e-d569aa70784e",
                  "service": null,
                  "order": 2,
                  "isCompressionEnabled": false,
                  "createdBy": "DATA_MIGRATION",
                  "modifiedBy": "DATA_MIGRATION",
                  "comment": null
              },
              {
                  "id": "702a49a1-6e1a-588d-9976-9577bffcc382",
                  "identifier_oldDoS_id": 600003,
                  "status": "active",
                  "connectionType": "email",
                  "name": null,
                  "payloadMimeType": "application/pdf",
                  "description": "Copy",
                  "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
                  "address": "another-test@nhs.net",
                  "managedByOrganisation": "98af3729-aed2-57e5-b65e-d569aa70784e",
                  "service": null,
                  "order": 3,
                  "isCompressionEnabled": false,
                  "createdBy": "DATA_MIGRATION",
                  "modifiedBy": "DATA_MIGRATION",
                  "comment": null
              }
          ]
      }
      """
