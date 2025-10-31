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

data "aws_security_group" "dms_replication_security_group" {
  name = "${var.project}-${var.environment}-*-etl-replication-sg"
}

data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = var.performance_ami_name_pattern
  }
  filter {
    name   = "architecture"
    values = var.performance_ami_architectures
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}
