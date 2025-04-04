module "dynamodb_tables" {
  source     = "../../modules/dynamodb"
  for_each   = var.dynamodb_tables
  table_name = "${local.prefix}-${each.key}${local.workspace_suffix}"

  hash_key  = each.value.hash_key
  range_key = each.value.range_key

  attributes = each.value.attributes
}
