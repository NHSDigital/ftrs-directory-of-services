@component
Feature: Locations - Search Locations

  As a user of the CRUD API
  I want to be able to update a location
  So that I can manage my locations in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Search locations (no data)
    When I call the CRUD API "GET /Location" endpoint

    # Bug - should return 200 with empty list, but currently returns 404
    Then the response status code should be 404
    And the response body should match the following JSON:
      """
      {
        "detail": "No locations found"
      }
      """

  Scenario: Search locations with data
    When I call the CRUD API "POST /Location" endpoint with the following JSON body:
      """
      {
        "name": "Test Location",
        "active": true,
        "address": {
          "line1": "123 Test Street",
          "line2": "Test District",
          "county": "Test County",
          "town": "Test Town",
          "postcode": "TE5 7ST"
        },
        "managingOrganisation": "00000000-0000-0000-0000-11111111111a",
        "primaryAddress": true
      }
      """
    Then the response status code should be 201
    And the "Location" header should be present in the response
    And the ID is extracted from the Location header as "location_id"
    And the "createdTime" value is extracted from the response body as "created_time"
    And the "lastUpdated" value is extracted from the response body as "last_updated_time"

    When I call the CRUD API "GET /Location" endpoint
    Then the response status code should be 200
    And the response body should match the following JSON:
      """
      [
        {
          "id": "{{location_id}}",
          "createdTime": "{{created_time}}",
          "lastUpdated": "{{last_updated_time}}",
          "createdBy": {
            "type": "app",
            "value": "SYSTEM",
            "display": "SYSTEM"
          },
          "lastUpdatedBy": {
            "type": "app",
            "value": "SYSTEM",
            "display": "SYSTEM"
          },
          "identifier_oldDoS_uid": null,
          "active": true,
          "address": {
            "line1": "123 Test Street",
            "line2": "Test District",
            "county": "Test County",
            "town": "Test Town",
            "postcode": "TE5 7ST"
          },
          "managingOrganisation": "00000000-0000-0000-0000-11111111111a",
          "name": "Test Location",
          "positionGCS": null,
          "positionReferenceNumber_UPRN": null,
          "positionReferenceNumber_UBRN": null,
          "primaryAddress": true,
          "partOf": null
        }
      ]
      """
