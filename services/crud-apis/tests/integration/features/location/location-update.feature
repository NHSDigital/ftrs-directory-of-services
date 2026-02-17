@component
Feature: Locations - Update Location

  As a user of the CRUD API
  I want to be able to update a location
  So that I can manage my locations in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Update a location with valid data
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

    When I call the CRUD API "PUT /Location/{{location_id}}" endpoint with the following JSON body:
      """
      {
        "id": "{{location_id}}",
        "name": "Updated Test Location",
        "active": false,
        "address": {
          "line1": "456 Updated Street",
          "line2": "Updated District",
          "county": "Updated County",
          "town": "Updated Town",
          "postcode": "UPD 4T3"
        },
        "managingOrganisation": "00000000-0000-0000-0000-11111111111a",
        "primaryAddress": false
      }
      """
    Then the response status code should be 200

    # Bug - createTime and lastUpdated are both overwritten on the update
    # They can also take any values from the API
    And the "createdTime" value is extracted from the response body as "updated_created_time"
    And the "lastUpdated" value is extracted from the response body as "updated_last_updated_time"

    And the response body should match the following JSON:
      """
      {
        "id": "{{location_id}}",
        "createdTime": "{{updated_created_time}}",
        "lastUpdated": "{{updated_last_updated_time}}",
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
        "active": false,
        "address": {
          "line1": "456 Updated Street",
          "line2": "Updated District",
          "county": "Updated County",
          "town": "Updated Town",
          "postcode": "UPD 4T3"
        },
        "managingOrganisation": "00000000-0000-0000-0000-11111111111a",
        "name": "Updated Test Location",
        "positionGCS": null,
        "positionReferenceNumber_UPRN": null,
        "positionReferenceNumber_UBRN": null,
        "primaryAddress": false,
        "partOf": null
      }
      """

  Scenario: Update a location that does not exist
    When I call the CRUD API "PUT /Location/00000000-0000-0000-0000-22222222222b" endpoint with the following JSON body:
      """
      {
        "id": "00000000-0000-0000-0000-22222222222b",
        "name": "Nonexistent Location",
        "active": true,
        "address": {
          "line1": "789 Nonexistent Street",
          "line2": "Nonexistent District",
          "county": "Nonexistent County",
          "town": "Nonexistent Town",
          "postcode": "NON 3X1"
        },
        "managingOrganisation": "00000000-0000-0000-0000-11111111111a",
        "primaryAddress": true
      }
      """

    # Bug - this should be handled gracefully
    Then the response status code should be 500
    And the response body should match the following JSON:
      """
      {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "error",
            "code": "exception",
            "diagnostics": "An unexpected error occurred"
          }
        ]
      }
      """

  Scenario: Update a location with invalid data
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

    When I call the CRUD API "PUT /Location/{{location_id}}" endpoint with the following JSON body:
      """
      {
        "id": "{{location_id}}",
        "name": "Test Location",
        "active": true,
        "address": null,
        "managingOrganisation": "00000000-0000-0000-0000-11111111111a",
        "primaryAddress": true
      }
      """
    Then the response status code should be 422
    And the response body should match the following JSON:
      """
      {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "error",
            "code": "invalid",
            "details": {
              "coding": [
                {
                  "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                  "code": "MSG_PARAM_INVALID",
                  "display": "Parameter content is invalid"
                }
              ],
              "text": "1 validation error:\n  {'type': 'model_attributes_type', 'loc': ('body', 'address'), 'msg': 'Input should be a valid dictionary or object to extract fields from', 'input': None}\n\n  File \"/Users/thomas/repos/github.com/NHSDigital/ftrs-directory-of-services/services/crud-apis/dos_ingest/router/location.py\", line 93, in update_location\n    PUT /Location/{location_id}"
            },
            "diagnostics": "1 validation error:\n  {'type': 'model_attributes_type', 'loc': ('body', 'address'), 'msg': 'Input should be a valid dictionary or object to extract fields from', 'input': None}\n\n  File \"/Users/thomas/repos/github.com/NHSDigital/ftrs-directory-of-services/services/crud-apis/dos_ingest/router/location.py\", line 93, in update_location\n    PUT /Location/{location_id}"
          }
        ]
      }
      """
