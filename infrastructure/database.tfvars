
dynamodb_tables = {
  "healthcare-service" = {
    hash_key  = "id"
    range_key = "field"
    attributes = [
      { name = "id", type = "S" },
      { name = "field", type = "S" }
    ]
    global_secondary_indexes = []
  }
  "organisation" = {
    hash_key  = "id"
    range_key = "field"
    attributes = [
      { name = "id", type = "S" },
      { name = "field", type = "S" },
      { name = "odscode", type = "S" }
    ]
    global_secondary_indexes = [
      {
        name            = "OdsCodeValueIndex"
        hash_key        = "odscode"
        projection_type = "ALL"
      }
    ]
  }
  "location" = {
    hash_key  = "id"
    range_key = "field"
    attributes = [
      { name = "id", type = "S" },
      { name = "field", type = "S" }
    ]
    global_secondary_indexes = []
  }
}

team_owner = "future-directory"
