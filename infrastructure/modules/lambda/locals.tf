# ==============================================================================
# Context

locals {
  workspace_suffix      = "${terraform.workspace}" == "default" ? "" : "${terraform.workspace}"
  environment_workspace = "${terraform.workspace}" == "default" ? "" : "${terraform.workspace}"
}
