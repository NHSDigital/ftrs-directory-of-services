@data-migration
Feature: Data Migration - Contraception Pharmacy

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  @happy
  Scenario: Contraception pharmacy migration when parent pharmacy has not been migrated yet
    # Parent pharmacy with ODS code FV493 exists in DoS but has NOT been migrated yet.
    # When the CON pharmacy is processed, the processor auto-migrates the parent first,
    # then creates the contraception HealthcareService linked to the parent org/location.
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 214249                                                   |
      | uid                                 | 2000130076                                               |
      | name                                | Boots - Tunbridge Wells                                  |
      | odscode                             | FV493                                                    |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          |                                                          |
      | telephonetriagereferralinstructions |                                                          |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 7-11 Calverley Road$Tunbridge Wells$Kent                 |
      | town                                | ROYAL TUNBRIDGE WELLS                                    |
      | postcode                            | TN1 2TE                                                  |
      | easting                             | 558506                                                   |
      | northing                            | 139690                                                   |
      | publicphone                         | 01892526486                                              |
      | nonpublicphone                      |                                                          |
      | fax                                 |                                                          |
      | email                               | 214249-fake@nhs.gov.uk                                   |
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
      | latitude                            | 51.1345483                                               |
      | longitude                           | 0.2641634                                                |
      | professionalreferralinfo            |                                                          |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |
    And a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 214250                                                   |
      | uid                                 | 2000130077                                               |
      | name                                | Contraception: Kent - Boots - Tunbridge Wells            |
      | odscode                             | FV493CON                                                 |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          |                                                          |
      | telephonetriagereferralinstructions |                                                          |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 7-11 Calverley Road$Tunbridge Wells$Kent                 |
      | town                                | ROYAL TUNBRIDGE WELLS                                    |
      | postcode                            | TN1 2TE                                                  |
      | easting                             | 558506                                                   |
      | northing                            | 139690                                                   |
      | publicphone                         | 01892526486                                              |
      | nonpublicphone                      |                                                          |
      | fax                                 |                                                          |
      | email                               | 214250-fake@nhs.gov.uk                                   |
      | web                                 | www.boots.com                                            |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2023-10-24 11:36:40.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                  |
      | lasttemplatename                    | *Service* Template - NHS Contraception (CON) R1.1        |
      | lasttemplateid                      | 221809                                                   |
      | typeid                              | 149                                                      |
      | parentid                            | 196814                                                   |
      | subregionid                         | 150021                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Boots                                                    |
      | latitude                            | 51.1345483                                               |
      | longitude                           | 0.2641634                                                |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    When the data migration process is run for table 'services', ID '214250' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 2 healthcare services created
    And the state table contains a record for key 'services#214250' with version 1

    # Validate that the CON healthcare service is linked to the auto-migrated parent org/location
    Then the 'healthcare-service' for service ID '214250' has content:
      """
      {
        "id": "65a233a9-2376-54cf-a84e-0f8ef38b6278",
        "identifier_oldDoS_uid": "2000130077",
        "providedBy": "c8acb753-8659-5d44-8123-d4118084cbf9",
        "location": "a2afd04f-d188-52ad-a60f-f42871f09ef4",
        "name": "Contraception: Kent - Boots - Tunbridge Wells",
        "category": "Pharmacy Services",
        "type": "Oral Contraception Prescription and Supply",
        "active": true
      }
      """

  @happy
  Scenario: Contraception pharmacy migration when parent pharmacy is already migrated
    # Parent pharmacy with ODS code FV494 is migrated first, establishing its org/location in state.
    # When the CON pharmacy is processed, the processor reuses the existing parent org/location IDs
    # directly from the state table — no second parent migration occurs.
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 214251                                                   |
      | uid                                 | 2000130074                                               |
      | name                                | Boots - Tonbridge                                        |
      | odscode                             | FV494                                                    |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          |                                                          |
      | telephonetriagereferralinstructions |                                                          |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 1 High Street$Tonbridge$Kent                             |
      | town                                | TONBRIDGE                                                |
      | postcode                            | TN9 1EJ                                                  |
      | easting                             | 558000                                                   |
      | northing                            | 146000                                                   |
      | publicphone                         | 01732123456                                              |
      | nonpublicphone                      |                                                          |
      | fax                                 |                                                          |
      | email                               | 214251-fake@nhs.gov.uk                                   |
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
      | latitude                            | 51.1000000                                               |
      | longitude                           | 0.2900000                                                |
      | professionalreferralinfo            |                                                          |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    # Migrate the parent pharmacy first so its state record and org/location exist in DynamoDB
    When the data migration process is run for table 'services', ID '214251' and method 'insert'

    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 214252                                                   |
      | uid                                 | 2000130073                                               |
      | name                                | Contraception: Kent - Boots - Tonbridge                  |
      | odscode                             | FV494CON                                                 |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          |                                                          |
      | telephonetriagereferralinstructions |                                                          |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 1 High Street$Tonbridge$Kent                             |
      | town                                | TONBRIDGE                                                |
      | postcode                            | TN9 1EJ                                                  |
      | easting                             | 558000                                                   |
      | northing                            | 146000                                                   |
      | publicphone                         | 01732123456                                              |
      | nonpublicphone                      |                                                          |
      | fax                                 |                                                          |
      | email                               | 214252-fake@nhs.gov.uk                                   |
      | web                                 | www.boots.com                                            |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2023-10-24 11:36:40.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                  |
      | lasttemplatename                    | *Service* Template - NHS Contraception (CON) R1.1        |
      | lasttemplateid                      | 221809                                                   |
      | typeid                              | 149                                                      |
      | parentid                            | 196814                                                   |
      | subregionid                         | 150021                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Boots                                                    |
      | latitude                            | 51.1000000                                               |
      | longitude                           | 0.2900000                                                |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    When the data migration process is run for table 'services', ID '214252' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 2 healthcare services created
    And the state table contains a record for key 'services#214252' with version 1

    # Validate that the CON healthcare service is linked to the already-migrated parent org/location
    Then the 'healthcare-service' for service ID '214252' has content:
      """
      {
        "id": "14d75a6f-a2e4-5efa-af91-cce032e846ec",
        "identifier_oldDoS_uid": "2000130073",
        "providedBy": "2eb4cde1-3a0d-547f-ab0d-cc5988e11ee0",
        "location": "9e8365fb-1b0a-50fa-97ab-ddd61c71f03d",
        "name": "Contraception: Kent - Boots - Tonbridge",
        "category": "Pharmacy Services",
        "type": "Oral Contraception Prescription and Supply",
        "active": true
      }
      """

  @rejection
  Scenario: Contraception pharmacy migration is rejected when parent pharmacy does not exist in DoS
    # No parent pharmacy with ODS code FV495 is seeded in DoS.
    # The processor raises ParentPharmacyNotFoundError and records an error — nothing is written
    # to DynamoDB and no state record is created.
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 214253                                                   |
      | uid                                 | 2000130072                                               |
      | name                                | Contraception: Kent - Boots - Sevenoaks                  |
      | odscode                             | FV495CON                                                 |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          |                                                          |
      | telephonetriagereferralinstructions |                                                          |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 2 London Road$Sevenoaks$Kent                             |
      | town                                | SEVENOAKS                                                |
      | postcode                            | TN13 1AX                                                 |
      | easting                             | 552000                                                   |
      | northing                            | 155000                                                   |
      | publicphone                         | 01732987654                                              |
      | nonpublicphone                      |                                                          |
      | fax                                 |                                                          |
      | email                               | 214253-fake@nhs.gov.uk                                   |
      | web                                 | www.boots.com                                            |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2023-10-24 11:36:40.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                  |
      | lasttemplatename                    | *Service* Template - NHS Contraception (CON) R1.1        |
      | lasttemplateid                      | 221809                                                   |
      | typeid                              | 149                                                      |
      | parentid                            | 196814                                                   |
      | subregionid                         | 150021                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Boots                                                    |
      | latitude                            | 51.2000000                                               |
      | longitude                           | 0.1900000                                                |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    When the data migration process is run for table 'services', ID '214253' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 0 transformed, 0 inserted, 0 updated, 0 skipped and 1 errors
    And no organisation was created for service '214253'
    And no location was created for service '214253'
    And no healthcare service was created for service '214253'
