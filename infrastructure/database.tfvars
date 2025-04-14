
dynamodb_tables = {
  "healthcare-service" = {
    hash_key  = "id"
    range_key = "field"
    attributes = [
      { name = "id", type = "S" },
      { name = "field", type = "S" }
    ]
  }
  "organisation" = {
    hash_key  = "id"
    range_key = "field"
    attributes = [
      { name = "id", type = "S" },
      { name = "field", type = "S" }
    ]
  }
  "location" = {
    hash_key  = "id"
    range_key = "field"
    attributes = [
      { name = "id", type = "S" },
      { name = "field", type = "S" }
    ]
  }
}

team_owner = "fd"
