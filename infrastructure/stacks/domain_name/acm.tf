resource "aws_acm_certificate" "custom_domain_api_cert" {
  count             = var.environment == "mgmt" ? 0 : 1
  domain_name       = "*.${var.environment}.${var.root_domain_name}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${local.resource_prefix}-api${local.workspace_suffix}-certificate"
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = var.environment == "mgmt" ? {} : {
    for dvo in aws_acm_certificate.custom_domain_api_cert[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }

  zone_id = aws_route53_zone.environment_zone[0].zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]
}

resource "aws_acm_certificate_validation" "custom_domain_api_cert_validation" {
  count = var.environment == "mgmt" ? 0 : 1

  certificate_arn         = aws_acm_certificate.custom_domain_api_cert[0].arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]

  timeouts {
    create = "5m"
  }
}
