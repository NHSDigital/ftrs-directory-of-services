data "aws_acm_certificate" "vpn_cert" {
  count = var.environment == "dev" ? 1 : 0

  domain      = "${local.account_prefix}-vpn"
  types       = ["IMPORTED"]
  statuses    = ["ISSUED"]
  most_recent = true
}

data "aws_iam_role" "account_github_runner_role_name" {
  name = "${var.repo_name}-${var.account_github_runner_role_name}"
}
