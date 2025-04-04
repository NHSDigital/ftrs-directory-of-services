module "dynamodb_table" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "3.3.0"

  name                = "${var.table_name}${local.workspace_suffix}"
  hash_key            = var.hash_key
  range_key           = var.range_key
  autoscaling_enabled = var.autoscaling_enabled
  stream_enabled      = var.stream_enabled
  stream_view_type    = var.stream_view_type
  attributes          = var.attributes
  billing_mode        = var.billing_mode

  server_side_encryption_enabled = true
}
