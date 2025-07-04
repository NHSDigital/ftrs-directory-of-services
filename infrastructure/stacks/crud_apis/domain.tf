data "aws_route53_zone" "main" {
  name = local.root_domain_name
}

data "aws_acm_certificate" "domain_cert" {
  domain      = "*.${local.root_domain_name}"
  statuses    = ["ISSUED"]
  most_recent = true
}

resource "aws_apigatewayv2_domain_name" "api_domain" {
  domain_name = "TEMP-${local.workspace_suffix}.*.${local.root_domain_name}"

  domain_name_configuration {
    # certificate_arn = var.mtls_certificate_arn != "" ? var.mtls_certificate_arn : aws_acm_certificate.api_cert[0].arn
    certificate_arn = data.aws_acm_certificate.domain_cert.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  tags = {
    Name = "${local.resource_prefix}-api-gateway${local.workspace_suffix}-domain"
  }
}

resource "aws_apigatewayv2_api_mapping" "api_mapping" {
  api_id      = module.api_gateway.api_id
  domain_name = aws_apigatewayv2_domain_name.api_domain.id
  stage       = module.api_gateway.stage_id
}

resource "aws_route53_zone" "api_record" {
  name = "TEMP-${local.workspace_suffix}.${local.root_domain_name}"
}
