module "api_gateway" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2.git?ref=c62c315eeab078913c51d7d6a5eb722f4c1e82f5"
  # version = 5.3.1
  # https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest
  name          = "${local.resource_prefix}-api-gateway${local.workspace_suffix}"
  description   = "FtRS Service Search API Gateway"
  protocol_type = "HTTP"
  # TODO: To be disabled after APIM integration
  # disable_execute_api_endpoint = true

  create_domain_name    = false
  create_domain_records = false

  # cors_configuration = {
  #   allow_headers = ["content-type", "x-amz-date", "authorization", "x-api-key", "x-amz-security-token", "x-amz-user-agent"]
  #   allow_methods = ["*"]
  #   allow_origins = ["*"]
  # }

  # SSL Cert:
  # NB. I think the module will only support TLS_1.2 and an endpoint_type of REGIONAL.
  domain_name                 = "servicesearch${local.workspace_suffix}.${local.root_domain_name}"
  domain_name_certificate_arn = data.aws_acm_certificate.domain_cert.arn

  # Mtls
  mutual_tls_authentication = {
    truststore_uri = "s3://${local.s3_trust_store_bucket_name}/${local.trust_store_file_path}"
  }

  routes = {
    "GET /Organization" = {
      integration = {
        uri                    = module.organisation_api_lambda.lambda_function_arn
        payload_format_version = var.api_gateway_payload_format_version
        timeout_milliseconds   = var.api_gateway_integration_timeout
      }
    }
  }

  stage_access_log_settings = {
    create_log_group            = true
    log_group_retention_in_days = var.api_gateway_access_logs_retention_days
    format = jsonencode({
      context = {
        domainName              = "$context.domainName"
        integrationErrorMessage = "$context.integrationErrorMessage"
        protocol                = "$context.protocol"
        requestId               = "$context.requestId"
        requestTime             = "$context.requestTime"
        responseLength          = "$context.responseLength"
        routeKey                = "$context.routeKey"
        stage                   = "$context.stage"
        status                  = "$context.status"
        error = {
          message      = "$context.error.message"
          responseType = "$context.error.responseType"
        }
        identity = {
          sourceIP = "$context.identity.sourceIp"
        }
        integration = {
          error             = "$context.integration.error"
          integrationStatus = "$context.integration.integrationStatus"
        }
      }
    })
  }

  stage_default_route_settings = {
    detailed_metrics_enabled = true
    xray_tracing_enabled     = true
    #   triggers = {
    #     redeployment = sha1(jsonencode([
    #       module.search_rest_api
    #     ]))
    # }
  }
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
