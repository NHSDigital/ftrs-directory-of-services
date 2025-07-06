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

data "aws_ec2_managed_prefix_list" "s3_prefix_list" {
  name = "com.amazonaws.${var.aws_region}.s3"
}

data "aws_ec2_managed_prefix_list" "dynamodb_prefix_list" {
  name = "com.amazonaws.${var.aws_region}.dynamodb"
}

# Fetch AWS public IP ranges for eu-west-2
data "aws_ip_ranges" "eu_west_2_public" {
  regions  = ["eu-west-2"]
  services = ["AMAZON"]
}
