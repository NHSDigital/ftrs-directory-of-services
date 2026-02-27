@data-migration
Feature: Data Migration - Blood Pressure Check Pharmacy

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  @happy
  Scenario: Blood pressure check pharmacy migration when parent pharmacy has not been migrated yet
    # Parent pharmacy with ODS code FV496 exists in DoS but has NOT been migrated yet.
    # When the BPS pharmacy is processed, the processor auto-migrates the parent first,
    # then creates the BP check HealthcareService linked to the parent org/location.
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 214254                                                   |
      | uid                                 | 2000130078                                               |
      | name                                | Boots - Maidstone                                        |
      | odscode                             | FV496                                                    |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          |                                                          |
      | telephonetriagereferralinstructions |                                                          |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 45-47 High Street$Maidstone$Kent                         |
      | town                                | MAIDSTONE                                                |
      | postcode                            | ME14 1SR                                                 |
      | easting                             | 575506                                                   |
      | northing                            | 155690                                                   |
      | publicphone                         | 01622756789                                              |
      | nonpublicphone                      |                                                          |
      | fax                                 |                                                          |
      | email                               | 214254-fake@nhs.gov.uk                                   |
      | web                                 | www.boots.com                                            |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2023-10-24 11:36:40.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                  |
      | lasttemplatename                    | Pharmacy Template                                        |
      | lasttemplateid                      | 221808                                                   |
      | typeid                              | 13                                                       |
      | parentid                            | 196814                                                   |
      | subregionid                         | 150021                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Boots                                                    |
      | latitude                            | 51.2700483                                               |
      | longitude                           | 0.5231634                                                |
      | professionalreferralinfo            |                                                          |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |
    And a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 214255                                                   |
      | uid                                 | 2000130079                                               |
      | name                                | BP Check: Kent - Boots - Maidstone                       |
      | odscode                             | FV496BPS                                                 |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          |                                                          |
      | telephonetriagereferralinstructions |                                                          |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 45-47 High Street$Maidstone$Kent                         |
      | town                                | MAIDSTONE                                                |
      | postcode                            | ME14 1SR                                                 |
      | easting                             | 575506                                                   |
      | northing                            | 155690                                                   |
      | publicphone                         | 01622756789                                              |
      | nonpublicphone                      |                                                          |
      | fax                                 |                                                          |
      | email                               | 214255-fake@nhs.gov.uk                                   |
      | web                                 | www.boots.com                                            |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2023-10-24 11:36:40.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                  |
      | lasttemplatename                    | *Service* Template - NHS Blood Pressure Check (BPS) R1.0 |
      | lasttemplateid                      | 221810                                                   |
      | typeid                              | 148                                                      |
      | parentid                            | 196814                                                   |
      | subregionid                         | 150021                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Boots                                                    |
      | latitude                            | 51.2700483                                               |
      | longitude                           | 0.5231634                                                |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    When the data migration process is run for table 'services', ID '214255' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 2 healthcare services created
    And the state table contains a record for key 'services#214255' with version 1

    # Validate that the BPS healthcare service is linked to the auto-migrated parent org/location
    Then the 'healthcare-service' for service ID '214255' has content:
      """
      {
        "id": "525130cd-2ebd-526c-a5c5-95cbb96756b2",
        "identifier_oldDoS_uid": "2000130079",
        "providedBy": "32d3c101-574f-5f20-af27-8a4ba6ce6d14",
        "location": "6e3e03a6-a694-52af-b156-939066cd29d8",
        "name": "BP Check: Kent - Boots - Maidstone",
        "category": "Pharmacy Services",
        "type": "Essential Services",
        "active": true
      }
      """

  @happy
  Scenario: Blood pressure check pharmacy migration when parent pharmacy is already migrated
    # Parent pharmacy with ODS code FV497 is migrated first, establishing its org/location in state.
    # When the BPS pharmacy is processed, the processor reuses the existing parent org/location IDs
    # directly from the state table — no second parent migration occurs.
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 214256                                                   |
      | uid                                 | 2000130080                                               |
      | name                                | Boots - Canterbury                                       |
      | odscode                             | FV497                                                    |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          |                                                          |
      | telephonetriagereferralinstructions |                                                          |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 8 St Margaret's Street$Canterbury$Kent                   |
      | town                                | CANTERBURY                                               |
      | postcode                            | CT1 2TG                                                  |
      | easting                             | 615000                                                   |
      | northing                            | 157000                                                   |
      | publicphone                         | 01227456123                                              |
      | nonpublicphone                      |                                                          |
      | fax                                 |                                                          |
      | email                               | 214256-fake@nhs.gov.uk                                   |
      | web                                 | www.boots.com                                            |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2023-10-24 11:36:40.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                  |
      | lasttemplatename                    | Pharmacy Template                                        |
      | lasttemplateid                      | 221808                                                   |
      | typeid                              | 13                                                       |
      | parentid                            | 196814                                                   |
      | subregionid                         | 150021                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Boots                                                    |
      | latitude                            | 51.2800000                                               |
      | longitude                           | 1.0800000                                                |
      | professionalreferralinfo            |                                                          |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    # Migrate the parent pharmacy first so its state record and org/location exist in DynamoDB
    When the data migration process is run for table 'services', ID '214256' and method 'insert'

    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 214257                                                   |
      | uid                                 | 2000130081                                               |
      | name                                | BP Check: Kent - Boots - Canterbury                      |
      | odscode                             | FV497BPS                                                 |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          |                                                          |
      | telephonetriagereferralinstructions |                                                          |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 8 St Margaret's Street$Canterbury$Kent                   |
      | town                                | CANTERBURY                                               |
      | postcode                            | CT1 2TG                                                  |
      | easting                             | 615000                                                   |
      | northing                            | 157000                                                   |
      | publicphone                         | 01227456123                                              |
      | nonpublicphone                      |                                                          |
      | fax                                 |                                                          |
      | email                               | 214257-fake@nhs.gov.uk                                   |
      | web                                 | www.boots.com                                            |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2023-10-24 11:36:40.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                  |
      | lasttemplatename                    | *Service* Template - NHS Blood Pressure Check (BPS) R1.0 |
      | lasttemplateid                      | 221810                                                   |
      | typeid                              | 148                                                      |
      | parentid                            | 196814                                                   |
      | subregionid                         | 150021                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Boots                                                    |
      | latitude                            | 51.2800000                                               |
      | longitude                           | 1.0800000                                                |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    When the data migration process is run for table 'services', ID '214257' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 2 healthcare services created
    And the state table contains a record for key 'services#214257' with version 1

    # Validate that the BPS healthcare service is linked to the already-migrated parent org/location
    Then the 'healthcare-service' for service ID '214257' has content:
      """
      {
        "id": "6b18b304-45d6-5d67-a218-d9ea2aee0476",
        "identifier_oldDoS_uid": "2000130081",
        "providedBy": "8533b4f4-d0e7-505c-b833-98cba2de250e",
        "location": "8e29f663-a2af-5657-9834-234efbc7bd89",
        "name": "BP Check: Kent - Boots - Canterbury",
        "category": "Pharmacy Services",
        "type": "Essential Services",
        "active": true
      }
      """

  @rejection
  Scenario: Blood pressure check pharmacy migration is rejected when parent pharmacy does not exist in DoS
    # No parent pharmacy with ODS code FV498 is seeded in DoS.
    # The processor raises ParentPharmacyNotFoundError and records an error — nothing is written
    # to DynamoDB and no state record is created.
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 214258                                                   |
      | uid                                 | 2000130082                                               |
      | name                                | BP Check: Kent - Boots - Ashford                         |
      | odscode                             | FV498BPS                                                 |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          |                                                          |
      | telephonetriagereferralinstructions |                                                          |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 32 High Street$Ashford$Kent                              |
      | town                                | ASHFORD                                                  |
      | postcode                            | TN24 8TQ                                                 |
      | easting                             | 601000                                                   |
      | northing                            | 142000                                                   |
      | publicphone                         | 01233621987                                              |
      | nonpublicphone                      |                                                          |
      | fax                                 |                                                          |
      | email                               | 214258-fake@nhs.gov.uk                                   |
      | web                                 | www.boots.com                                            |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2023-10-24 11:36:40.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                  |
      | lasttemplatename                    | *Service* Template - NHS Blood Pressure Check (BPS) R1.0 |
      | lasttemplateid                      | 221810                                                   |
      | typeid                              | 148                                                      |
      | parentid                            | 196814                                                   |
      | subregionid                         | 150021                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Boots                                                    |
      | latitude                            | 51.1500000                                               |
      | longitude                           | 0.8700000                                                |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    When the data migration process is run for table 'services', ID '214258' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 0 transformed, 0 inserted, 0 updated, 0 skipped and 1 errors
    And no organisation was created for service '214258'
    And no location was created for service '214258'
    And no healthcare service was created for service '214258'
