@data-migration
Feature:Data Migration Hello World

  Scenario:Happy path migration for a GP Practice
    Given the data migration system is ready
    * record for 'organisation' from 'tests/resources/migration/output_samples/organisation-with_endpoints.dynamo.json' is loaded
    When I run the hello world data migration test
    Then the 'organisation' for service ID '8752ab74-e8b3-569a-92ed-a0dcdc44d22e' has content:
      """
      {
        "id":"8752ab74-e8b3-569a-92ed-a0dcdc44d22e",
        "active":true,
        "field":"document",
        "identifier_ODS_ODSCode":"P81036",
        "name":"Peel House Medical Practice",
        "createdDateTime":"2025-01-01T00:00:00Z",
        "createdBy":"DATA_MIGRATION",
        "modifiedDateTime":"2025-01-01T00:00:00",
        "modifiedBy":"DATA_MIGRATION",
        "type":"GP Practice",
        "telecom":null,
        "endpoints":[
          {
            "address":"dummy-endpoint-email@nhs.net",
            "connectionType":"email",
            "createdBy":"DATA_MIGRATION",
            "createdDateTime":"2025-10-07T08:38:32.840760Z",
            "description":"Copy",
            "id":"1c322b99-b5f9-5780-afa7-2c43c6b46256",
            "identifier_oldDoS_id":366198,
            "isCompressionEnabled":false,
            "managedByOrganisation":"8752ab74-e8b3-569a-92ed-a0dcdc44d22e",
            "modifiedBy":"DATA_MIGRATION",
            "modifiedDateTime":"2025-10-07T08:38:32.840760Z",
            "name":null,
            "order":2,
            "payloadMimeType":"application/pdf",
            "payloadType":"urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service":null,
            "status":"active"
          },
          {
            "address":"https://dummy-itk-endpoint.nhs.uk",
            "connectionType":"itk",
            "createdBy":"DATA_MIGRATION",
            "createdDateTime":"2024-10-07T08:38:32.840760Z",
            "description":"Primary",
            "id":"1cac4fb9-55d9-58ad-aa07-ef2a1da15433",
            "identifier_oldDoS_id":203479,
            "isCompressionEnabled":false,
            "managedByOrganisation":"8752ab74-e8b3-569a-92ed-a0dcdc44d22e",
            "modifiedBy":"DATA_MIGRATION",
            "modifiedDateTime":"2025-10-07T08:38:32.840760Z",
            "name":null,
            "order":1,
            "payloadMimeType":"application/hl7-cda+xml",
            "payloadType":"urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
            "service":null,
            "status":"active"
          },
          {
            "address":"dummy-endpoint-email@nhs.net",
            "connectionType":"email",
            "createdBy":"DATA_MIGRATION",
            "createdDateTime":"2025-10-07T08:38:32.840760Z",
            "description":"Primary",
            "id":"07e79ade-a657-5fa7-94b9-cf9815edfbf5",
            "identifier_oldDoS_id":311751,
            "isCompressionEnabled":false,
            "managedByOrganisation":"8752ab74-e8b3-569a-92ed-a0dcdc44d22e",
            "modifiedBy":"DATA_MIGRATION",
            "modifiedDateTime":"2025-10-07T08:38:32.840760Z",
            "name":null,
            "order":2,
            "payloadMimeType":"application/pdf",
            "payloadType":"urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
            "service":null,
            "status":"active"
          },
          {
            "address":"https://dummy-itk-endpoint.nhs.uk",
            "connectionType":"itk",
            "createdBy":"DATA_MIGRATION",
            "createdDateTime":"2025-10-07T08:38:32.840760Z",
            "description":"Copy",
            "id":"cbcddf9d-eda7-591c-b806-6cd96dde1736",
            "identifier_oldDoS_id":366197,
            "isCompressionEnabled":false,
            "managedByOrganisation":"8752ab74-e8b3-569a-92ed-a0dcdc44d22e",
            "modifiedBy":"DATA_MIGRATION",
            "modifiedDateTime":"2025-10-07T08:38:32.840760Z",
            "name":null,
            "order":1,
            "payloadMimeType":"application/hl7-cda+xml",
            "payloadType":"urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
            "service":null,
            "status":"active"
          }
        ]
      }
      """
    Then there are 1 organisation, 0 location and 0 healthcare services created
