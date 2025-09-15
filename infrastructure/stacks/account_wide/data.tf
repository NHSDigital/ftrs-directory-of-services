data "aws_acm_certificate" "vpn_cert" {
  count = var.environment == "dev" ? 1 : 0

  domain      = "${local.account_prefix}-vpn"
  types       = ["IMPORTED"]
  statuses    = ["ISSUED"]
  most_recent = true
}

data "aws_availability_zones" "available_azs" {
  state = "available"
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

data "aws_iam_role" "app_github_runner_iam_role" {
  name = "${var.repo_name}-${var.app_github_runner_role_name}"
}
