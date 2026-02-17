@component
Feature: Organisations - Search

  As a user of the CRUD API
  I want to be able to search for organisations by their ODS code
  So that I can find relevant organisations in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Search for all organisations (no organisations exist)
    When I call the CRUD API "GET /Organization" endpoint
    Then the response status code should be 200
    And the response body should match the following JSON:
      """
      {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 0,
        "entry": []
      }
      """

  Scenario: Search for organisations by ODS code (no matching organisations)
    When I call the CRUD API "GET /Organization?identifier=https://fhir.nhs.uk/Id/ods-organization-code|NONEXISTENT" endpoint


    # TODO: Should be an empty searchset bundle, not an OperationOutcome
    #
    # **FHIR Docs**
    # Where the content of the parameter is syntactically incorrect, servers SHOULD return an error.
    #
    # However, where the issue is a logical condition (e.g. unknown subject or code), the server SHOULD process the search,
    # including processing the parameter - with the result of returning an empty search set, since the parameter cannot be satisfied.
    #
    # In such cases, the search process MAY include an OperationOutcome in the search set that contains additional hints
    # and warnings about the search process. This is included in the search results as an entry with search mode = outcome.
    # Clients can use this information to improve future searches.
    #
    Then the response status code should be 404
    And the response body should match the following JSON:
      """
      {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "error",
            "code": "not-found",
            "details": {
              "coding": [
                {
                  "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                  "code": "MSG_NO_EXIST",
                  "display": "Resource does not exist"
                }
              ],
              "text": "Organisation with ODS code 'NONEXISTENT' not found"
            },
            "diagnostics": "Organisation with ODS code 'NONEXISTENT' not found"
          }
        ]
      }
      """


  Scenario: Search for all organisations
    Given all organisations are created from the test data files

    When I call the CRUD API "GET /Organization" endpoint
    Then the response status code should be 200
    # There's a bug here - total should be the total number of matched results, not amount returned in response

    And the "entry[*].resource.id" value is extracted from the response body as "resource_ids"

  # Can't enforce a proper assertion here, as order of results is not guaranteed
  # And the response body should match the following JSON:
  #   """
  #   {
  #     "resourceType": "Bundle",
  #     "type": "searchset",
  #     "total": 10,
  #     "entry": [
  #       {
  #         "resource": {
  #           "active": true,
  #           "id": "{{resource_ids[0]}}",
  #           "identifier": [
  #             {
  #               "system": "https://fhir.nhs.uk/Id/ods-organization-code",
  #               "use": "official",
  #               "value": "X98765"
  #             }
  #           ],
  #           "meta": {
  #             "profile": [
  #               "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
  #             ]
  #           },
  #           "name": "Village Surgery & Health Centre",
  #           "resourceType": "Organization",
  #           "telecom": [
  #             {
  #               "system": "phone",
  #               "value": "01603 123456"
  #             },
  #             {
  #               "system": "phone",
  #               "value": "01603 123457"
  #             },
  #             {
  #               "system": "email",
  #               "value": "surgery@villagehealth.nhs.uk"
  #             }
  #           ]
  #         }
  #       }
  #     ]
  #   }
  #   """

  Scenario: Search for organisations by ODS code
    Given all organisations are created from the test data files
    When I call the CRUD API "GET /Organization?identifier=https://fhir.nhs.uk/Id/ods-organization-code|X98765" endpoint
    Then the response status code should be 200
    And the "entry[0].resource.id" value is extracted from the response body as "resource_id"
    And the response body should match the following JSON:
      """
      {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 1,
        "entry": [
          {
            "resource": {
              "active": true,
              "id": "{{resource_id}}",
              "identifier": [
                {
                  "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                  "use": "official",
                  "value": "X98765"
                }
              ],
              "meta": {
                "profile": [
                  "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
                ]
              },
              "name": "Village Surgery & Health Centre",
              "resourceType": "Organization",
              "telecom": [
                {
                  "system": "phone",
                  "value": "01603 123456"
                },
                {
                  "system": "phone",
                  "value": "01603 123457"
                },
                {
                  "system": "email",
                  "value": "surgery@villagehealth.nhs.uk"
                }
              ]
            }
          }
        ]
      }
      """
