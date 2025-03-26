data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${var.main_project}-${var.environment}-vpc"]
  }
}