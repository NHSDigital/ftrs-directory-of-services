module "search_rest_api" {
  source = "../../modules/api-gateway-rest-api"

  rest_api_name = "${local.resource_prefix}-api-gateway"
}

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = module.search_rest_api.rest_api_id
  lifecycle {
    create_before_destroy = true
  }
  depends_on = [
    aws_api_gateway_method.search_get,
    aws_api_gateway_resource.search_resource
  ]
  triggers = {
    redeployment = sha1(jsonencode([
      module.search_rest_api
    ]))
  }
}

# trivy:ignore:AVD-AWS-0001 : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-407
resource "aws_api_gateway_stage" "stage" {
  # checkov:skip=CKV_AWS_76: TODO https://nhsd-jira.digital.nhs.uk/browse/DOSIS-1840
  # checkov:skip=CKV_AWS_120: TODO https://nhsd-jira.digital.nhs.uk/browse/DOSIS-1840
  # checkov:skip=CKV2_AWS_4: TODO https://nhsd-jira.digital.nhs.uk/browse/DOSIS-1840
  # checkov:skip=CKV2_AWS_51: TODO https://nhsd-jira.digital.nhs.uk/browse/DOSIS-1840
  depends_on           = [aws_cloudwatch_log_group.api_gateway_execution_logs]
  deployment_id        = aws_api_gateway_deployment.deployment.id
  rest_api_id          = module.search_rest_api.rest_api_id
  stage_name           = "default"
  xray_tracing_enabled = true
}

resource "aws_cloudwatch_log_group" "api_gateway_execution_logs" {
  # checkov:skip=CKV_AWS_158: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-404
  # checkov:skip=CKV_AWS_338: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-404
  name              = "/aws/apigateway/${local.resource_prefix}-api-gateway-execution-logs${local.workspace_suffix}/default"
  retention_in_days = var.retention_in_days
}

resource "aws_api_gateway_domain_name" "api_custom_domain" {
  domain_name              = "servicesearch${local.workspace_suffix}.${local.root_domain_name}"
  regional_certificate_arn = data.aws_acm_certificate.domain_cert.arn
  security_policy          = "TLS_1_2"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  mutual_tls_authentication {
    truststore_uri = "s3://${local.s3_trust_store_bucket_name}/${local.trust_store_file_path}"
  }
}

resource "aws_api_gateway_base_path_mapping" "mapping" {
  api_id      = module.search_rest_api.rest_api_id
  stage_name  = aws_api_gateway_stage.stage.stage_name
  domain_name = aws_api_gateway_domain_name.api_custom_domain.domain_name
}

resource "aws_route53_record" "gpsearch_api_a_alias" {
  zone_id = data.aws_route53_zone.dev_ftrs_cloud.zone_id
  name    = "servicesearch${local.workspace_suffix}.${local.root_domain_name}"
  type    = "A"
  alias {
    name                   = aws_api_gateway_domain_name.api_custom_domain.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.api_custom_domain.regional_zone_id
    evaluate_target_health = false
  }
}
