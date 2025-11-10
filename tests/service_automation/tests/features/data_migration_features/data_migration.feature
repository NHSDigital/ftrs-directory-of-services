@data-migration
Feature:Data Migration Hello World
  Scenario:Happy path migration for a GP Practice
     Given a "Service" exists in DoS with attributes
    | key                 | value                       |
    | id                  | 5752                        |
    | uid                 | 138179                      |
    | name                | Abbey Medical Practice, Evesham, Worcestershire |
    | odscode             | M81094                      |
    | openallhours        | FALSE                       |
    | publicreferralinstructions | STUB Public Referral Instruction Text Field 5752 |
    | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 5752 |
    | restricttoreferrals | TRUE                        |
    | address             | Evesham Medical Centre$Abbey Lane$Evesham |
    | town                | EVESHAM                     |
    | postcode            | WR11 4BS                    |
    | easting             | 403453                      |
    | northing            | 243634                      |
    | publicphone         | 01386 761111                |
    | nonpublicphone      | 99999 000000                |
    | fax                 | 77777 000000                |
    | email               |                             |
    | web                 | www.abbeymedical.com        |
    | createdby           | HUMAN                       |
    | createdtime         | 00:51.0                     |
    | modifiedby          | HUMAN                       |
    | modifiedtime        | 55:23.0                     |
    | lasttemplatename    | Midlands template R46 Append PC |
    | lasttemplateid      | 244764                      |
    | typeid              | 100                         |
    | parentid            | 150013                      |
    | subregionid         | 150013                      |
    | statusid            | 1                           |
    | organisationid      |                             |
    | returnifopenminutes |                             |
    | publicname          | Abbey Medical Practice      |
    | latitude            | 52.0910543                  |
    | longitude           | -1.951003                   |
    | professionalreferralinfo | Non-public numbers are for healthcare professionals ONLY; they are not for routine contact and must not be shared with patients.
    * GP practice opening hours are 08:00-18:30, hours shown on DoS may vary for administration purposes."|
    | lastverified        |                             |
    | nextverificationdue |                             |
    | partition_name      | (id >= 1 AND id <= 12340)   |
		*	(id >= 1 AND id <= 12340)
    When data migration is executed
    Then the 'organisation' for service ID '36fce427-0f31-4a4e-903f-74dcf9e63cfd' has content:
      """
      {
        "id": "36fce427-0f31-4a4e-903f-74dcf9e63cfd",
        "createdBy": "ROBOT",
        "createdDateTime": "2025-06-27T12:46:36.111296Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2025-06-27T12:46:36.111296Z",
        "identifier_ODS_ODSCode": "M00081046",
        "active": true,
        "name": "Abbottswood Medical Practice, Pershore, Worcestershire",
        "telecom": null,
        "type": "GP Practice",
        "endpoints": [
          {
            "id": "d449e3b8-eba2-43ec-9ee5-aee85387b53d",
            "createdBy": "ROBOT",
            "createdDateTime": "2025-06-27T12:46:36.111296Z",
            "modifiedBy": "ROBOT",
            "modifiedDateTime": "2025-06-27T12:46:36.111296Z",
            "identifier_oldDoS_id": 212417,
            "status": "active",
            "connectionType": "email",
            "name": null,
            "payloadMimeType": "application/pdf",
            "description": "Primary",
            "payloadType": "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
            "address": "dummy-endpoint-email@nhs.net",
            "managedByOrganisation": "36fce427-0f31-4a4e-903f-74dcf9e63cfd",
            "service": null,
            "order": 2,
            "isCompressionEnabled": false
          },
          {
            "id": "6b2077f2-23b3-4d65-8a72-cb58b26e42d1",
            "createdBy": "ROBOT",
            "createdDateTime": "2025-06-27T12:46:36.111296Z",
            "modifiedBy": "ROBOT",
            "modifiedDateTime": "2025-06-27T12:46:36.111296Z",
            "identifier_oldDoS_id": 212415,
            "status": "active",
            "connectionType": "email",
            "name": null,
            "payloadMimeType": "application/pdf",
            "description": "Copy",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "address": "dummy-endpoint-email@nhs.net",
            "managedByOrganisation": "36fce427-0f31-4a4e-903f-74dcf9e63cfd",
            "service": null,
            "order": 2,
            "isCompressionEnabled": false
          },
          {
            "id": "93e43c4a-a199-4927-97b7-34200b59955e",
            "createdBy": "ROBOT",
            "createdDateTime": "2025-06-27T12:46:36.111296Z",
            "modifiedBy": "ROBOT",
            "modifiedDateTime": "2025-06-27T12:46:36.111296Z",
            "identifier_oldDoS_id": 212413,
            "status": "active",
            "connectionType": "itk",
            "name": null,
            "payloadMimeType": "application/hl7-cda+xml",
            "description": "Copy",
            "payloadType": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "address": "https://dummy-itk-endpoint.nhs.uk",
            "managedByOrganisation": "36fce427-0f31-4a4e-903f-74dcf9e63cfd",
            "service": null,
            "order": 1,
            "isCompressionEnabled": false
          },
          {
            "id": "1a0b103c-77b6-472a-91c9-fd0e4895b85c",
            "createdBy": "ROBOT",
            "createdDateTime": "2025-06-27T12:46:36.111296Z",
            "modifiedBy": "ROBOT",
            "modifiedDateTime": "2025-06-27T12:46:36.111296Z",
            "identifier_oldDoS_id": 214755,
            "status": "active",
            "connectionType": "itk",
            "name": null,
            "payloadMimeType": "application/hl7-cda+xml",
            "description": "Primary",
            "payloadType": "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
            "address": "https://dummy-itk-endpoint.nhs.uk",
            "managedByOrganisation": "36fce427-0f31-4a4e-903f-74dcf9e63cfd",
            "service": null,
            "order": 1,
            "isCompressionEnabled": false
          }
        ]
      }
      """
    Then there is 1 organisation, 0 location and 0 healthcare services created
