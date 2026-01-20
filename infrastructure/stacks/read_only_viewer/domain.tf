resource "aws_route53_record" "read_only_viewer_record" {
  count   = local.stack_enabled
  zone_id = data.aws_route53_zone.main[0].zone_id
  name    = "${var.stack_name}${local.workspace_suffix}.${local.env_domain_name}"
  type    = "A"

  alias {
    name                   = module.read_only_viewer_cloudfront[0].cloudfront_distribution_domain_name
    zone_id                = module.read_only_viewer_cloudfront[0].cloudfront_distribution_hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "read_only_viewer_record_ipv6" {
  count   = local.stack_enabled
  zone_id = data.aws_route53_zone.main[0].zone_id
  name    = "${var.stack_name}${local.workspace_suffix}.${local.env_domain_name}"
  type    = "AAAA"

  alias {
    name                   = module.read_only_viewer_cloudfront[0].cloudfront_distribution_domain_name
    zone_id                = module.read_only_viewer_cloudfront[0].cloudfront_distribution_hosted_zone_id
    evaluate_target_health = false
  }
}
