@data-migration
Feature: Data Migration

  # Background:
  # Given the test environment is configured
  # And the DoS database has test data
  # And DynamoDB tables are ready

  Scenario: Triage codes are migrated
    When triage code full migration is executed
    Then the triage code migration process completes successfully
    Then field 'source' on table 'triage-code' for id 'SD8002' and field sort key 'item' has content:
      """
      {
        "source": "pathways"
      }
      """
    Then field 'source' on table 'triage-code' for id 'SD11000' and field sort key 'item' has content:
      """
      {
        "source": "servicefinder"
      }
      """
    Then the 'triage-code' for id 'SD4311' and field sort key 'item' has content:
      """
      {
        "codeType": "Symptom Discriminator (SD)",
        "synonyms": [],
        "createdDateTime": "2025-11-24T20:48:08.669768Z",
        "source": "pathways",
        "codeValue": "PC extended ophthalmic assessment and management capability, minor condition (MECS)",
        "codeID": 4311,
        "combinations": [],
        "field": "item",
        "zCodeExists": false,
        "dx_group_ids": [],
        "createdBy": "SYSTEM",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-11-24T20:48:08.669775Z",
        "id": "SD4311",
        "time": 0
      }
      """
    Then the 'triage-code' for id 'SD14023' and field sort key 'item' has content:
      """
      {
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
        "createdDateTime": "2025-11-26T07:50:50.602490Z",
        "source": "servicefinder",
        "codeValue": "GP Practice",
        "codeID": 14023,
        "combinations": [],
        "field": "item",
        "zCodeExists": false,
        "dx_group_ids": [],
        "createdBy": "SYSTEM",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-11-26T07:50:50.602496Z",
        "id": "SD14023",
        "time": 0
      }
      """
    Then the 'triage-code' for id 'DX08' and field sort key 'item' has content:
      """
      {
        "codeType": "Disposition (Dx)",
        "synonyms": [],
        "createdDateTime": "2025-11-27T08:26:02.927515Z",
        "source": "pathways",
        "codeValue": "To contact a Primary Care Service within 24 hours",
        "codeID": "DX08",
        "combinations": [],
        "field": "item",
        "zCodeExists": false,
        "dx_group_ids": [],
        "createdBy": "SYSTEM",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-11-27T08:26:02.927523Z",
        "id": "DX08",
        "time": 1440
      }
      """
    Then the 'triage-code' for id 'SG360' and field sort key 'item' has content:
      """
      {
        "codeType": "Symptom Group (SG)",
        "synonyms": [],
        "createdDateTime": "2025-11-26T07:50:29.278874Z",
        "source": "servicefinder",
        "codeValue": "z2.0 - Service Types",
        "codeID": 360,
        "combinations": [],
        "field": "item",
        "zCodeExists": true,
        "dx_group_ids": [],
        "createdBy": "SYSTEM",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-11-26T07:50:29.278878Z",
        "id": "SG360",
        "time": 0
      }
      """
    Then the 'triage-code' for id 'SD11843' and field sort key 'item' has content:
      """
      {
        "codeType": "Symptom Discriminator (SD)",
        "synonyms": [],
        "createdDateTime": "2025-11-26T07:50:48.851428Z",
        "source": "servicefinder",
        "codeValue": "Cancer Support Service",
        "codeID": 11843,
        "combinations": [],
        "field": "item",
        "zCodeExists": false,
        "dx_group_ids": [],
        "createdBy": "SYSTEM",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-11-26T07:50:48.851434Z",
        "id": "SD11843",
        "time": 0
      }
      """

    Then the 'triage-code' for id 'SG1240' and field sort key 'item' has content:
      """
      {
        "codeType": "Symptom Group (SG)",
        "synonyms": [],
        "createdDateTime": "2025-11-24T20:47:52.801548Z",
        "source": "pathways",
        "codeValue": "Self Triage, Mental Health",
        "codeID": 1240,
        "combinations": [],
        "field": "item",
        "zCodeExists": false,
        "dx_group_ids": [],
        "createdBy": "SYSTEM",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-11-24T20:47:52.801553Z",
        "id": "SG1240",
        "time": 0
      }
      """
    Then the 'triage-code' for id 'SG1240' and field sort key 'combinations' has content:
      """
      {
        "codeType": "Symptom Group and Symptom Discriminator Pair (SG-SD)",
        "synonyms": [],
        "createdDateTime": "2025-11-24T20:48:36.304817Z",
        "source": "pathways",
        "codeValue": null,
        "codeID": null,
        "combinations": [
          {
            "value": "AMB toxic ingestion",
            "id": "SD4019"
          },
          {
            "value": "AMB new/worsening breathlessness",
            "id": "SD4033"
          },
          {
            "value": "ED full ED assessment and management capability",
            "id": "SD4052"
          },
          {
            "value": "AMB pregnancy",
            "id": "SD4032"
          },
          {
            "value": "AMB chest pain (undifferentiated)",
            "id": "SD4086"
          },
          {
            "value": "AMB diabetes mellitus",
            "id": "SD4099"
          },
          {
            "value": "AMB toxic inhalation",
            "id": "SD4023"
          },
          {
            "value": "AMB stroke",
            "id": "SD4028"
          },
          {
            "value": "AMB palpitations",
            "id": "SD4097"
          },
          {
            "value": "AMB decreased conscious level",
            "id": "SD4108"
          },
          {
            "value": "AMB fit/convulsion",
            "id": "SD4048"
          },
          {
            "value": "AMB associated injury, risk",
            "id": "SD4136"
          },
          {
            "value": "PC mental health assessment, alcohol misuse",
            "id": "SD4180"
          },
          {
            "value": "RP ED alcohol withdrawl",
            "id": "SD4547"
          },
          {
            "value": "RP ED self harm",
            "id": "SD4554"
          },
          {
            "value": "Major Trauma",
            "id": "SD4428"
          },
          {
            "value": "RP ED headache",
            "id": "SD4575"
          },
          {
            "value": "RP AMB features of severe illness",
            "id": "SD4370"
          },
          {
            "value": "RP ED intoxication",
            "id": "SD4334"
          },
          {
            "value": "RP AMB fit or seizure within past 12 hours",
            "id": "SD4338"
          },
          {
            "value": "RP ED behaviour problem",
            "id": "SD4349"
          },
          {
            "value": "RP AMB meningitis",
            "id": "SD4360"
          },
          {
            "value": "RP AMB suicide attempt",
            "id": "SD4364"
          },
          {
            "value": "ED mental health crisis",
            "id": "SD4419"
          },
          {
            "value": "PC full mental health assessment capability",
            "id": "SD4456"
          },
          {
            "value": "AMB critical illness assessment",
            "id": "SD4459"
          },
          {
            "value": "AMB recent head injury",
            "id": "SD4098"
          },
          {
            "value": "AMB drug/alcohol/solvent misuse",
            "id": "SD4030"
          }
        ],
        "field": "combinations",
        "zCodeExists": false,
        "dx_group_ids": [],
        "createdBy": "SYSTEM",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-11-24T20:48:36.304824Z",
        "id": "SG1240",
        "time": 0
      }
      """
