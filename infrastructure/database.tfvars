
dynamodb_tables = {
  "healthcare-service" = {
    hash_key  = "id"
    range_key = "field"
    attributes = [
      { name = "id", type = "S" },
      { name = "field", type = "S" },
      { name = "location", type = "S" },
      { name = "providedBy", type = "S" },
    ]
    global_secondary_indexes = [
      {
        name            = "LocationIndex"
        hash_key        = "location"
        projection_type = "ALL"
      },
      {
        name            = "ProvidedByIndex"
        hash_key        = "providedBy"
        projection_type = "ALL"
      }

    ]
  }
  "organisation" = {
    hash_key  = "id"
    range_key = "field"
    attributes = [
      { name = "id", type = "S" },
      { name = "field", type = "S" },
      { name = "identifier_ODS_ODSCode", type = "S" }
    ]
    global_secondary_indexes = [
      {
        name            = "OdsCodeValueIndex"
        hash_key        = "identifier_ODS_ODSCode"
        projection_type = "ALL"
      }
    ]
  }
  "location" = {
    hash_key  = "id"
    range_key = "field"
    attributes = [
      { name = "id", type = "S" },
      { name = "field", type = "S" },
      { name = "managingOrganisation", type = "S" }
    ]
    global_secondary_indexes = [
      {
        name            = "ManagingOrganisationIndex"
        hash_key        = "managingOrganisation"
        projection_type = "ALL"
      }
    ]
  }
}

team_owner = "future-directory"
