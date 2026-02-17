@component
Feature: Locations - Delete Location

  As a user of the CRUD API
  I want to be able to delete a location
  So that I can manage my locations in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Delete a valid location
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

    When I call the CRUD API "GET /Location/{{location_id}}" endpoint
    Then the response status code should be 200

    When I call the CRUD API "DELETE /Location/{{location_id}}" endpoint
    Then the response status code should be 204

    When I call the CRUD API "GET /Location/{{location_id}}" endpoint
    Then the response status code should be 404

  Scenario: Delete a location with a non-existent ID
    When I call the CRUD API "DELETE /Location/00000000-0000-0000-0000-00000000000a" endpoint
    Then the response status code should be 404
    And the response body should match the following JSON:
      """
      {
        "detail": "Location not found"
      }
      """
