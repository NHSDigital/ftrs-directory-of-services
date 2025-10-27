resource "aws_route53_record" "ui_record" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${var.stack_name}${local.workspace_suffix}.${local.env_domain_name}"
  type    = "A"

  alias {
    name                   = module.ui_cloudfront.cloudfront_distribution_domain_name
    zone_id                = module.ui_cloudfront.cloudfront_distribution_hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "ui_record_ipv6" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${var.stack_name}${local.workspace_suffix}.${local.env_domain_name}"
  type    = "AAAA"

  alias {
    name                   = module.ui_cloudfront.cloudfront_distribution_domain_name
    zone_id                = module.ui_cloudfront.cloudfront_distribution_hosted_zone_id
    evaluate_target_health = false
  }
}
