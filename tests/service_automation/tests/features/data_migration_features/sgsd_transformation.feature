@data-migration
Feature: Data Migration

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Symptom groups and symptom discriminators are transformed
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  |                                                     9001533 |
      | uid                                 |                                                      113474 |
      | name                                | GP: Redlam Surgery - Blackburn                              |
      | odscode                             | P81061                                                      |
      | isnational                          |                                                             |
      | openallhours                        | false                                                       |
      | publicreferralinstructions          |                                                             |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 1533 |
      | restricttoreferrals                 | true                                                        |
      | address                             | Redlam Surgery$62-64 Redlam$Blackburn$Lancashire            |
      | town                                | BLACKBURN                                                   |
      | postcode                            | BB2 1UW                                                     |
      | easting                             |                                                      366856 |
      | northing                            |                                                      427476 |
      | publicphone                         |                                                 01254260051 |
      | nonpublicphone                      |                                                             |
      | fax                                 |                                                00000 666666 |
      | email                               |                                        1533-fake@nhs.gov.uk |
      | web                                 | https://www.redlamsurgery.co.uk/                            |
      | createdby                           | HUMAN                                                       |
      | createdtime                         |                                     2011-06-17 09:19:36.000 |
      | modifiedby                          | ROBOT                                                       |
      | modifiedtime                        |                                     2025-02-11 16:32:18.000 |
      | lasttemplatename                    | BwD GP Update 08 01 25                                      |
      | lasttemplateid                      |                                                      245697 |
      | typeid                              |                                                         100 |
      | parentid                            |                                                        1527 |
      | subregionid                         |                                                        1527 |
      | statusid                            |                                                           1 |
      | organisationid                      |                                                             |
      | returnifopenminutes                 |                                                             |
      | publicname                          | Redlam Surgery - Blackburn                                  |
      | latitude                            |                                                  53.7426167 |
      | longitude                           |                                                  -2.5039993 |
      | professionalreferralinfo            |                                                             |
      | lastverified                        |                                                             |
      | nextverificationdue                 |                                                             |
    And a "ServiceSGSD" exists in DoS with attributes
      | key       | value     | comment          |
      | id        | 100000001 |                  |
      | serviceid |   9001533 |                  |
      | sdid      |      4003 |                  |
      | sgid      |      1006 | null zcodeexists |
    And a "ServiceSGSD" exists in DoS with attributes
      | key       | value     |                  |
      | id        | 100000002 |                  |
      | serviceid |   9001533 |                  |
      | sdid      |     14020 |                  |
      | sgid      |       360 | true zcodeexists |
    And a "ServiceSGSD" exists in DoS with attributes
      | key       | value     |                   |
      | id        | 100000003 |                   |
      | serviceid |   9001533 |                   |
      | sdid      |      4003 |                   |
      | sgid      |      1228 | false zcodeexists |
    And a "ServiceSGSD" exists in DoS with attributes
      | key       | value     |              |
      | id        | 100000004 |              |
      | serviceid |   9001533 |              |
      | sdid      |     14023 | has synonyms |
      | sgid      |       360 |              |
    When the data migration process is run for table 'services', ID '9001533' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then the 'healthcare-service' for id 'db9ce3d2-d7cc-5e0f-bb95-d1e63c59a7ef' has content:
      """
      {
          "id": "db9ce3d2-d7cc-5e0f-bb95-d1e63c59a7ef",
          "field": "document",
          "active": true,
          "ageEligibilityCriteria": null,
          "category": "GP Services",
          "createdBy": "DATA_MIGRATION",
          "createdDateTime": "2025-11-14T14:31:54.666870Z",
          "dispositions": [],
          "identifier_oldDoS_uid": "113474",
          "location": "a31ced93-0801-5653-8bb1-beb875bc60c8",
          "migrationNotes": [
              "field:['email'] ,error: not_nhs_email,message:Email address is not a valid NHS email address,value:1533-fake@nhs.gov.uk",
              "field:['nonpublicphone'] ,error: empty,message:Phone number cannot be empty,value:None"
          ],
          "modifiedBy": "DATA_MIGRATION",
          "modifiedDateTime": "2025-11-14T14:31:54.666870Z",
          "name": "GP: Redlam Surgery - Blackburn",
          "openingTime": [],
          "providedBy": "dfab9d49-584d-5096-87aa-5ce1afc3d067",
          "symptomGroupSymptomDiscriminators": [
              {
                  "sg": {
                      "codeID": 1006,
                      "id": "7ac04bbf-06bb-5c0b-a956-21558a59b94c",
                      "source": "pathways",
                      "codeType": "Symptom Group (SG)",
                      "codeValue": "Abdominal, Flank, Groin or Back Pain or Swelling"
                  },
                  "sd": {
                      "codeID": 4003,
                      "id": "300af504-ba5d-5973-a877-a0789c6863ab",
                      "source": "pathways",
                      "codeType": "Symptom Discriminator (SD)",
                      "synonyms": [],
                      "codeValue": "PC full Primary Care assessment and prescribing capability"
                  }
              },
              {
                  "sg": {
                      "codeID": 360,
                      "id": "39ce1220-2586-5b2e-a35d-3021b2e0337c",
                      "source": "servicefinder",
                      "codeType": "Symptom Group (SG)",
                      "codeValue": "z2.0 - Service Types"
                  },
                  "sd": {
                      "codeID": 14020,
                      "id": "3f6333f8-d4f2-5528-a2d8-5925da018905",
                      "source": "servicefinder",
                      "codeType": "Symptom Discriminator (SD)",
                      "synonyms": [],
                      "codeValue": "GP Choice"
                  }
              },
              {
                  "sg": {
                      "codeID": 1228,
                      "id": "9e4a3d4b-5f15-5002-9fb2-a2529752f2a7",
                      "source": "pathways",
                      "codeType": "Symptom Group (SG)",
                      "codeValue": "Self-Harm"
                  },
                  "sd": {
                      "codeID": 4003,
                      "id": "300af504-ba5d-5973-a877-a0789c6863ab",
                      "source": "pathways",
                      "codeType": "Symptom Discriminator (SD)",
                      "synonyms": [],
                      "codeValue": "PC full Primary Care assessment and prescribing capability"
                  }
              },
              {
                  "sg": {
                      "codeID": 360,
                      "id": "39ce1220-2586-5b2e-a35d-3021b2e0337c",
                      "source": "servicefinder",
                      "codeType": "Symptom Group (SG)",
                      "codeValue": "z2.0 - Service Types"
                  },
                  "sd": {
                      "codeID": 14023,
                      "id": "6ce70d41-9337-578d-a662-d9fe25016d40",
                      "source": "servicefinder",
                      "codeType": "Symptom Discriminator (SD)",
                      "synonyms": [
                          "General Practice",
                          "Long Covid",
                          "Post Covid",
                          "GP Surgery",
                          "Doctors Surgery",
                          "Primary Care",
                          "GP In Hours"
                      ],
                      "codeValue": "GP Practice"
                  }
              }
          ],
          "telecom": {
              "email": null,
              "phone_private": null,
              "phone_public": "01254260051",
              "web": "https://www.redlamsurgery.co.uk/"
          },
          "type": "GP Consultation Service"
      }
      """
