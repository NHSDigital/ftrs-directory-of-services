module "dynamodb_table" {
  # Module version: 3.3.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table.git?ref=03b38ee3c52250c7d606f6a21e04624a41be52f7"


  name                           = "${var.table_name}${local.workspace_suffix}"
  hash_key                       = var.hash_key
  range_key                      = var.range_key
  autoscaling_enabled            = var.autoscaling_enabled
  stream_enabled                 = var.stream_enabled
  stream_view_type               = var.stream_view_type
  attributes                     = var.attributes
  billing_mode                   = var.billing_mode
  point_in_time_recovery_enabled = var.point_in_time_recovery_enabled

  server_side_encryption_enabled = true

  global_secondary_indexes = var.global_secondary_indexes
}
