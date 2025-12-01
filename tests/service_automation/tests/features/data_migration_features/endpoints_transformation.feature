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
                  "status": "active"
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
                  "status": "active"
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
                  "status": "active"
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
                  "status": "active"
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
                  "status": "active"
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
                  "status": "active"
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
