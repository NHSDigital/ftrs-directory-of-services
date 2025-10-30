module "dynamodb_table" {
  # Module version: 4.3.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table.git?ref=1ab93ca82023b72fe37de7f17cc10714867b2d4f"

  name                           = "${var.table_name}${local.workspace_suffix}"
  hash_key                       = var.hash_key
  range_key                      = var.range_key
  autoscaling_enabled            = var.autoscaling_enabled
  stream_enabled                 = var.stream_enabled
  stream_view_type               = var.stream_view_type
  attributes                     = var.attributes
  billing_mode                   = var.billing_mode
  point_in_time_recovery_enabled = var.point_in_time_recovery_enabled
  ttl_enabled                    = var.ttl_enabled
  ttl_attribute_name             = var.ttl_attribute_name

  server_side_encryption_enabled = true

  global_secondary_indexes = var.global_secondary_indexes
}
