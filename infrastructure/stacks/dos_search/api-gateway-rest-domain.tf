resource "aws_api_gateway_domain_name" "domain_name" {
  domain_name = "servicesearch${local.workspace_suffix}.${local.root_domain_name}"

  security_policy          = var.api_gateway_tls_security_policy
  regional_certificate_arn = data.aws_acm_certificate.issued_domain_certificate.arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  mutual_tls_authentication {
    truststore_uri = "s3://${local.s3_trust_store_bucket_name}/${local.trust_store_file_path}"
  }
}

resource "aws_route53_record" "domain_r53" {
  name    = aws_api_gateway_domain_name.domain_name.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.hosted_zone.zone_id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.domain_name.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.domain_name.regional_zone_id
  }
}

resource "aws_api_gateway_base_path_mapping" "domain_mapping" {
  api_id      = aws_api_gateway_rest_api.api_gateway.id
  domain_name = aws_api_gateway_domain_name.domain_name.domain_name
  stage_name  = aws_api_gateway_stage.default.stage_name
}

data "aws_acm_certificate" "issued_domain_certificate" {
  domain   = "*.${local.root_domain_name}"
  statuses = ["ISSUED"]
}

data "aws_route53_zone" "hosted_zone" {
  name = local.root_domain_name
}
