# ==============================================================================
# Context

locals {
  workspace_suffix      = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  environment_workspace = "${terraform.workspace}" == "default" ? "" : "${terraform.workspace}"
  additional_json_policies = (concat(var.policy_jsons, [
    data.aws_iam_policy_document.allow_private_subnet_policy.json,
    data.aws_iam_policy_document.limit_to_environment_vpc_policy.json,
    data.aws_iam_policy_document.enforce_vpc_lambda_policy.json,
    data.aws_iam_policy_document.deny_lambda_function_access_policy.json,
    data.aws_iam_policy_document.vpc_access_policy.json
  ]))
}
