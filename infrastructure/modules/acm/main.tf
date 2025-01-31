# Request the certificate
resource "aws_acm_certificate" "cm" {
  domain_name               = var.domain_name
  validation_method         = "DNS"
  subject_alternative_names = var.san_list
  tags                      = var.tags

  lifecycle {
    create_before_destroy = true
  }
}

# Create DNS validation records in Route 53
resource "aws_route53_record" "cm" {
  for_each = {
    for dvo in aws_acm_certificate.cm.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }

  allow_overwrite = true
  zone_id         = var.zone_id
  name            = each.value.name
  type            = each.value.type
  records         = [each.value.record]
  ttl             = 300
}

output "certificate_arn" {
  value = aws_acm_certificate.cm.arn
}
