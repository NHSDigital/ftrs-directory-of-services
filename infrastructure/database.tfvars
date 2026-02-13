
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
  "triage-code" = {
    hash_key  = "id"
    range_key = "field"
    attributes = [
      { name = "id", type = "S" },
      { name = "field", type = "S" },
      { name = "codeType", type = "S" },
    ]
    global_secondary_indexes = [
      {
        name            = "CodeTypeIndex"
        hash_key        = "codeType"
        range_key       = "id"
        projection_type = "ALL"
      }
    ]
    stream_enabled = false
  }
  "version-history" = {
    hash_key  = "entity_id"
    range_key = "timestamp"
    attributes = [
      { name = "entity_id", type = "S" },
      { name = "timestamp", type = "S" }
    ]
    global_secondary_indexes = []
  }
}

team_owner = "future-directory"

version_history_lambda_runtime      = "python3.12"
version_history_lambda_name         = "version-history-lambda"
version_history_lambda_handler      = "version_history.lambda_handler.lambda_handler"
version_history_lambda_timeout      = 30
version_history_lambda_memory_size  = 256
version_history_batch_size          = 10
version_history_maximum_concurrency = 2
