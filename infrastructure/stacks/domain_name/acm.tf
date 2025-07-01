resource "aws_acm_certificate" "api_cert" {
  # count             = var.create_certificate && var.mtls_certificate_arn == "" ? 1 : 0
  domain_name       = "TEMP-${local.workspace_suffix}.${var.environment}.ftrs.cloud.nhs.uk"
  validation_method = "DNS"

  subject_alternative_names = [
    "*.TEMP-${local.workspace_suffix}.${var.environment}.ftrs.cloud.nhs.uk"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "${local.resource_prefix}-api-gateway${local.workspace_suffix}-certificate"
    Environment = var.environment
  }
}

# Create DNS validation records
resource "aws_route53_record" "cert_validation" {
  # for_each = var.create_certificate && var.mtls_certificate_arn == "" ? {
  for_each = {
    for dvo in aws_acm_certificate.api_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
    # } : {}
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = var.hosted_zone_id
}

# Validate the certificate
resource "aws_acm_certificate_validation" "api_cert" {
  # count                   = var.create_certificate && var.mtls_certificate_arn == "" ? 1 : 0
  certificate_arn         = aws_acm_certificate.api_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]

  timeouts {
    create = "5m"
  }
}

output "certificate_arn" {
  value = aws_acm_certificate.api_cert.arn
}

output "aws_acm_certificate_validation_cert" {
  value = aws_acm_certificate_validation.api_cert
}
