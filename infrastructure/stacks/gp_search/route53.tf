resource "aws_route53_zone" "gp_search_subdomain" {
  name = var.subdomain_fqdn
}
