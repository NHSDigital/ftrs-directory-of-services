data "aws_route53_zone" "main" {
  name = local.root_domain_name
}

data "aws_acm_certificate" "domain_cert" {
  domain      = "*.${local.root_domain_name}"
  statuses    = ["ISSUED"]
  most_recent = true
}

data "aws_acm_certificate" "domain_cert" {
  domain      = "*.${local.root_domain_name}"
  statuses    = ["ISSUED"]
  most_recent = true
}

resource "aws_apigatewayv2_domain_name" "api_domain" {
  domain_name = "api${local.workspace_suffix}.${local.root_domain_name}"

  domain_name_configuration {
    # certificate_arn = var.mtls_certificate_arn != "" ? var.mtls_certificate_arn : aws_acm_certificate.api_cert[0].arn
    certificate_arn = data.aws_acm_certificate.domain_cert.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  mutual_tls_authentication {
    truststore_uri = "s3://${local.s3_trust_store_bucket_name}/${local.trust_store_file_path}"
    # truststore_version = "EpDjR6hSPsWm10QColTqhzY61Vi8lLkC"
  }

  tags = {
    Name = "${local.resource_prefix}-api-gateway${local.workspace_suffix}-domain"
  }
}

resource "aws_apigatewayv2_api_mapping" "api_mapping" {
  api_id          = module.api_gateway.api_id
  domain_name     = aws_apigatewayv2_domain_name.api_domain.id
  stage           = module.api_gateway.stage_id
  api_mapping_key = "crud"
}

resource "aws_route53_record" "api_record" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "$api${local.workspace_suffix}.${local.root_domain_name}"
  type    = "A"
  alias {
    name                   = aws_apigatewayv2_domain_name.api_domain.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.api_domain.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}
