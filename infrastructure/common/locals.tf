locals {
  account_id       = data.aws_caller_identity.current.id
  workspace_suffix = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  artefacts_bucket = "${var.repo_name}-mgmt-${var.artefacts_bucket_name}"
  resource_prefix  = "${var.project}-${var.environment}-${var.stack_name}"
  account_prefix   = "${var.repo_name}-${var.environment}"

  # TODO remove once no longer used - use resource_prefix instead
  prefix = "${var.project}-${var.environment}"
  # Deploy databases only in default Terraform workspace.
  # This ensures that database resources are provisioned only in the intended environment.
  deploy_databases = "default" == "${terraform.workspace}"
}
