data "aws_iam_role" "app_github_runner_iam_role" {
  name = "${var.repo_name}-${var.app_github_runner_role_name}"
}

data "aws_ssm_parameter" "aws_account_id_dev" {
  name = "/dos/aws_account_id_dev"
}

data "aws_ssm_parameter" "aws_account_id_test" {
  name = "/dos/aws_account_id_test"
}

data "aws_ssm_parameter" "aws_account_id_prod" {
  name = "/dos/aws_account_id_prod"
}
