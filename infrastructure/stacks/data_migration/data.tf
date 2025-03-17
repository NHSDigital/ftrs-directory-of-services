data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${var.main_project}-${var.environment}-vpc"]
  }
}

data "aws_ec2_client_vpn_endpoint" "client_vpn_endpoint" {
  filter {
    name   = "tag:Project"
    values = ["${var.main_project}"]
  }
}

data "aws_security_group" "vpn_security_group" {
  name = "${var.main_project}-${var.environment}-vpn-sg"
}
