# ==============================================================================
# Context

locals {
  workspace_suffix = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
}
