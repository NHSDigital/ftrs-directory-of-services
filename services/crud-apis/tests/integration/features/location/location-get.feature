@component
Feature: Locations - Get Location

  As a user of the CRUD API
  I want to be able to get a location
  So that I can manage my locations in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Get a location with valid data
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

    When I call the CRUD API "GET /Location/{{location_id}}" endpoint
    Then the response status code should be 200
    And the response body should match the following JSON:
      """
      {
        "id": "{{location_id}}",
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
      """

  Scenario: Get a location with an invalid ID format
    When I call the CRUD API "GET /Location/invalid-uuid-format" endpoint
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
              "text": "1 validation error:\n  {'type': 'uuid_parsing', 'loc': ('path', 'location_id'), 'msg': 'Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1', 'input': 'invalid-uuid-format', 'ctx': {'error': 'invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1'}}\n\n  File \"/Users/thomas/repos/github.com/NHSDigital/ftrs-directory-of-services/services/crud-apis/dos_ingest/router/location.py\", line 15, in get_location_id\n    GET /Location/{location_id}"
            },
            "diagnostics": "1 validation error:\n  {'type': 'uuid_parsing', 'loc': ('path', 'location_id'), 'msg': 'Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1', 'input': 'invalid-uuid-format', 'ctx': {'error': 'invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1'}}\n\n  File \"/Users/thomas/repos/github.com/NHSDigital/ftrs-directory-of-services/services/crud-apis/dos_ingest/router/location.py\", line 15, in get_location_id\n    GET /Location/{location_id}"
          }
        ]
      }
      """

  Scenario: Get a location that does not exist
    When I call the CRUD API "GET /Location/00000000-0000-0000-0000-00000000000a" endpoint
    Then the response status code should be 404
    And the response body should match the following JSON:
      """
      {
        "detail": "Location not found"
      }
      """
