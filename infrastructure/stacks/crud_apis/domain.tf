data "aws_route53_zone" "main" {
  name = local.env_domain_name
}

data "aws_acm_certificate" "domain_cert" {
  domain      = "*.${local.env_domain_name}"
  statuses    = ["ISSUED"]
  most_recent = true
}

# trivy:ignore:AVD-AWS-0005 false positive – using API Gateway with TLS_1_2
resource "aws_api_gateway_domain_name" "crud_api_domain" {
  domain_name = "crud${local.workspace_suffix}.${local.env_domain_name}"

  security_policy          = var.api_gateway_tls_security_policy
  regional_certificate_arn = data.aws_acm_certificate.domain_cert.arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  mutual_tls_authentication {
    truststore_uri     = "s3://${local.s3_trust_store_bucket_name}/${local.trust_store_file_path}"
    truststore_version = data.aws_s3_object.truststore.version_id
  }

  tags = {
    Name = "${local.resource_prefix}-api-gateway${local.workspace_suffix}-domain"
  }
}

resource "aws_api_gateway_base_path_mapping" "domain_mapping" {
  api_id      = aws_api_gateway_rest_api.api_gateway.id
  domain_name = aws_api_gateway_domain_name.crud_api_domain.domain_name
  stage_name  = aws_api_gateway_stage.default.stage_name
}

resource "aws_route53_record" "api_record" {
  name    = aws_api_gateway_domain_name.crud_api_domain.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.main.zone_id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.crud_api_domain.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.crud_api_domain.regional_zone_id
  }
}
