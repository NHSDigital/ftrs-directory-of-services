# ==============================================================================
# Context

data "aws_caller_identity" "current" {}

locals {
  workspace_suffix = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  bucket_name      = var.environment == "prod" ? "${var.bucket_name}${local.workspace_suffix}-${data.aws_caller_identity.current.account_id}" : "${var.bucket_name}${local.workspace_suffix}"
}
