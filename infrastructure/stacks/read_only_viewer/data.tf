data "aws_iam_role" "github_runner_iam_role" {
  name = "${var.repo_name}-${var.github_runner_role_name}"
}
