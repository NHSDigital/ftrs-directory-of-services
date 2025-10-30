module "ui_session_store" {
  source = "../../modules/dynamodb"

  table_name         = "${local.resource_prefix}-session-store${local.workspace_suffix}"
  hash_key           = "sessionID"
  billing_mode       = "PAY_PER_REQUEST"
  ttl_attribute_name = "expiresAt"
  ttl_enabled        = true

  attributes = [
    {
      name = "sessionID"
      type = "S"
    },
    {
      name = "userID"
      type = "S"
    }
  ]

  global_secondary_indexes = [
    {
      name            = "UserIDIndex"
      hash_key        = "userID"
      projection_type = "KEYS_ONLY"
    }
  ]
}
