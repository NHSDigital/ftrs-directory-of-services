module "dynamodb_tables" {
  source     = "../../modules/dynamodb"
  for_each   = var.dynamodb_tables
  table_name = "${local.resource_prefix}-${each.key}"

  hash_key  = each.value.hash_key
  range_key = each.value.range_key

  attributes                     = each.value.attributes
  point_in_time_recovery_enabled = true
  stream_enabled                 = true

  global_secondary_indexes = lookup(each.value, "global_secondary_indexes", [])
}

module "version_history_table" {
  count  = var.version_history_enabled ? 1 : 0
  source = "../../modules/dynamodb"

  table_name                     = "${local.project_prefix}-database-version-history${local.workspace_suffix}"
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
