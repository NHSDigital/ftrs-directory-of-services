@component
Feature: HealthcareService - Search Healthcare Services

  As a user of the CRUD API
  I want to be able to update a location
  So that I can manage my locations in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Search healthcare services (no data)
    When I call the CRUD API "GET /HealthcareService" endpoint

    # Bug - should return 200 with empty list, but currently returns 404
    Then the response status code should be 404
    And the response body should match the following JSON:
      """
      {
        "detail": "No healthcare services found"
      }
      """

  Scenario: Search healthcare services with data
    When I call the CRUD API "POST /HealthcareService" endpoint with the following JSON body:
      """
      {
        "active": true,
        "category": "GP Services",
        "type": "GP Consultation Service",
        "providedBy": "00000000-0000-0000-0000-11111111111a",
        "location": "00000000-0000-0000-0000-11111111111b",
        "name": "Test Healthcare Service",
        "telecom": {
          "phone_public": "01234567890",
          "phone_private": null,
          "email": "test@nhs.net",
          "web": "https://www.nhs.uk"
        },
        "openingTime": null,
        "symptomGroupSymptomDiscriminators": [],
        "dispositions": [],
        "ageEligibilityCriteria": null
      }
      """

    Then the response status code should be 201
    And the "Location" header should be present in the response
    And the ID is extracted from the Location header as "healthcare_service_id"
    And the "createdTime" value is extracted from the response body as "created_time"
    And the "lastUpdated" value is extracted from the response body as "last_updated_time"

    When I call the CRUD API "GET /HealthcareService" endpoint
    Then the response status code should be 200
    And the response body should match the following JSON:
      """
      [
        {
          "id": "{{healthcare_service_id}}",
          "createdTime": "{{created_time}}",
          "createdBy": {
            "type": "app",
            "value": "SYSTEM",
            "display": "SYSTEM"
          },
          "lastUpdated": "{{last_updated_time}}",
          "lastUpdatedBy": {
            "type": "app",
            "value": "SYSTEM",
            "display": "SYSTEM"
          },
          "identifier_oldDoS_uid": null,
          "active": true,
          "category": "GP Services",
          "type": "GP Consultation Service",
          "providedBy": "00000000-0000-0000-0000-11111111111a",
          "location": "00000000-0000-0000-0000-11111111111b",
          "name": "Test Healthcare Service",
          "telecom": {
            "phone_public": "01234567890",
            "phone_private": null,
            "email": "test@nhs.net",
            "web": "https://www.nhs.uk"
          },
          "openingTime": null,
          "symptomGroupSymptomDiscriminators": [],
          "dispositions": [],
          "ageEligibilityCriteria": null
        }
      ]
      """
