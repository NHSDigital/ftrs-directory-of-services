module "state_table" {
  source = "../../modules/dynamodb"

  table_name                     = "${local.resource_prefix}-state"
  hash_key                       = "source_record_id"
  billing_mode                   = "PAY_PER_REQUEST"
  point_in_time_recovery_enabled = true

  attributes = [
    {
      name = "source_record_id"
      type = "S"
    }
  ]

  global_secondary_indexes = []
}

module "version_history_table" {
  source = "../../modules/dynamodb"

  table_name                     = "${local.resource_prefix}-version-history"
  hash_key                       = "entity_id"
  range_key                      = "timestamp"
  billing_mode                   = "PAY_PER_REQUEST"
  point_in_time_recovery_enabled = true

  attributes = [
    {
      name = "entity_id"
      type = "S"
    },
    {
      name = "timestamp"
      type = "S"
    }
  ]

  global_secondary_indexes = []
}
