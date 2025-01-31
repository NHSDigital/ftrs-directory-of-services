resource "aws_route53_zone" "cm" {
  name    = var.zone_name
  comment = var.comment
}
