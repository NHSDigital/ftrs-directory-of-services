resource "aws_route53_zone" "root_zone" {
  count = var.environment == "mgmt" ? 1 : 0
  name  = var.root_domain_name
}
