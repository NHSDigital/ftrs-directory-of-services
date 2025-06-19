resource "aws_route53_zone" "root_zone" {
  count = var.environment == "mgmt" ? 1 : 0
  name  = var.root_domain_name
}

resource "aws_route53_zone" "environment_zone" {
  count = var.environment == "mgmt" ? 0 : 1
  name  = "${var.environment}.${var.root_domain_name}"
}

# TODO: FDOS-401 We need to figure out cross-account IAM policies to allow this to work.
# data "aws_route53_zone" "root_zone" {
#   count = var.environment == "mgmt" ? 0 : 1
#   name  = var.root_domain_name
# }

# resource "aws_route53_record" "environment_zone_delegation" {
#   count   = var.environment == "mgmt" ? 0 : 1
#   zone_id = data.aws_route53_zone.root_zone[0].zone_id
#   name    = aws_route53_zone.environment_zone[0].name
#   type    = "NS"
#   ttl     = 300
#   records = aws_route53_zone.environment_zone[0].name_servers
# }
