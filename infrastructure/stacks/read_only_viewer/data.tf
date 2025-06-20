data "aws_iam_role" "app_github_runner_iam_role" {
  name = "${var.repo_name}-${var.app_github_runner_role_name}"
}

data "aws_ssm_parameter" "dos_aws_account_id_mgmt" {
  name = "/dos/${var.environment}/aws_account_id_mgmt"
}
