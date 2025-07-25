data "aws_route53_zone" "main" {
  name = local.env_domain_name
}

data "aws_acm_certificate" "domain_cert" {
  domain      = "*.${local.env_domain_name}"
  statuses    = ["ISSUED"]
  most_recent = true
}

resource "aws_apigatewayv2_domain_name" "crud_api_domain" {
  domain_name = "crud${local.workspace_suffix}.${local.env_domain_name}"

  domain_name_configuration {
    certificate_arn = data.aws_acm_certificate.domain_cert.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  mutual_tls_authentication {
    truststore_uri = "s3://${local.s3_trust_store_bucket_name}/${local.trust_store_file_path}"
  }

  tags = {
    Name = "${local.resource_prefix}-api-gateway${local.workspace_suffix}-domain"
  }
}

resource "aws_apigatewayv2_api_mapping" "api_mapping" {
  api_id      = module.api_gateway.api_id
  domain_name = aws_apigatewayv2_domain_name.crud_api_domain.id
  stage       = module.api_gateway.stage_id
}

resource "aws_route53_record" "api_record" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "crud${local.workspace_suffix}.${local.env_domain_name}"
  type    = "A"
  alias {
    name                   = aws_apigatewayv2_domain_name.crud_api_domain.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.crud_api_domain.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}
