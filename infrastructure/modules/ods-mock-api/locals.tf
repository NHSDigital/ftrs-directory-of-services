locals {
  vtl_template_path = "${path.module}/templates/ods_mock_basic.vtl"
  workspace_suffix  = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  stage_name        = "${var.environment}${local.workspace_suffix}"
}
