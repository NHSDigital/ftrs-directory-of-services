locals {
  account_id       = data.aws_caller_identity.current.id
  workspace_suffix = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  prefix           = "${var.project}-${var.environment}"
  artefacts_bucket = "${var.repo_name}-mgmt-${var.artefacts_bucket_name}"

  # Deploy databases only when the current environment matches the active Terraform workspace.
  # This ensures that database resources are provisioned only in the intended environment.
  deploy_databases = "default" == "${terraform.workspace}"
}
