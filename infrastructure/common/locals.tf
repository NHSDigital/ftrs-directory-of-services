locals {
  account_id       = data.aws_caller_identity.current.id
  workspace_suffix = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  prefix           = "${var.project}-${var.environment}"

  deploy_databases = var.environment == terraform.workspace
}
