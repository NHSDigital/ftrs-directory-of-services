module "dynamodb_tables" {
  source     = "../../modules/dynamodb"
  for_each   = toset(var.dynamodb_table_names)
  table_name = "${local.prefix}-${each.key}${local.workspace_suffix}"

  hash_key  = "id"
  range_key = "field"

  attributes = [
    {
      name = "id"
      type = "S"
    },
    {
      name = "field"
      type = "S"
    }
  ]
}
