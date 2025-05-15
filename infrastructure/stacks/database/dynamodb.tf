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
