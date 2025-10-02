locals {
  api_name      = format("%s-api-gateway%s", local.resource_prefix, local.workspace_suffix != "" ? local.workspace_suffix : "")
  api_log_group = format("/aws/apigateway/%s", local.api_name)
}

module "api_gateway" {
  source = "github.com/NHSDigital/ftrs-directory-of-services?ref=2cc250e/infrastructure/modules/api-gateway-v2-http"

  name        = local.api_name
  description = "FtRS Service Search API Gateway"

  # As soon as you tell the module to create a domain, the execute api endpoint will be disabled
  # so all routing will have to run through the domain (r53 route)
  # The module will create both A (IP4) and AAAA (IP6) records
  # HTTP API Gateways support TLS v1.2 and 1.3 only (https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-ciphers.html)
  create_domain_name    = true
  create_domain_records = true
  hosted_zone_name      = local.env_domain_name
  domain_name           = "servicesearch${local.workspace_suffix}.${local.env_domain_name}"

  # We do not need to create a certificate because we are using a shared one, specified in the domain_name_certificate_arn
  domain_certificate_arn = data.aws_acm_certificate.domain_cert.arn
  mtls_truststore_uri    = "s3://${local.s3_trust_store_bucket_name}/${local.trust_store_file_path}"

  # JP - At some point we may want to implement CORS
  # cors_configuration = {
  #   allow_headers = ["content-type", "x-amz-date", "authorization", "x-api-key", "x-amz-security-token", "x-amz-user-agent"]
  #   allow_methods = ["*"]
  #   allow_origins = ["*"]
  # }

  routes = {
    "GET /Organization" = {
      integration = {
        uri                    = module.lambda.lambda_function_arn
        payload_format_version = var.api_gateway_payload_format_version
        timeout_milliseconds   = var.api_gateway_integration_timeout
      }
    }
    "GET /_status" = {
      integration = {
        uri                    = module.health_check_lambda.lambda_function_arn
        payload_format_version = var.api_gateway_payload_format_version
        timeout_milliseconds   = var.api_gateway_integration_timeout
      }
    }
  }

  stage_access_log_settings = {
    create_log_group            = true
    log_group_name              = local.api_log_group
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
  }
}
