locals {
  version_history_enabled = var.version_history_enabled ? 1 : 0

  table_streams = { for table_name in ["organisation", "location", "healthcare-service"] :
    table_name => {
      stream_arn = module.dynamodb_tables[table_name].dynamodb_table_stream_arn
      table_arn  = module.dynamodb_tables[table_name].dynamodb_table_arn
    }
  }
}
