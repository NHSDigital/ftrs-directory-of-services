module "api_gateway" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2.git?ref=c62c315eeab078913c51d7d6a5eb722f4c1e82f5"
  # version = 5.3.1
  # https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest
  name          = "${local.resource_prefix}-api-gateway${local.workspace_suffix}"
  description   = "FtRS Service Search API Gateway"
  protocol_type = "HTTP"

  # As soon as you tell the module to create a domain, the execute api endpoint will be disabled
  # so all routing will have to run through the domain (r53 route)
  # The module will create both A (IP4) and AAAA (IP6) records
  # HTTP API Gateways support TLS v1.2 and 1.3 only (https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-ciphers.html)
  create_domain_name    = true
  create_domain_records = true
  hosted_zone_name      = local.env_domain_name
  domain_name           = "servicesearch${local.workspace_suffix}.${local.env_domain_name}"

  # We do not need to create a certificate because we are using a shared one, specified in the domain_name_certificate_arn
  create_certificate          = false
  domain_name_certificate_arn = data.aws_acm_certificate.domain_cert.arn

  mutual_tls_authentication = {
    truststore_uri = "s3://${local.s3_trust_store_bucket_name}/${local.trust_store_file_path}"
  }

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
  }

  stage_default_route_settings = {
    detailed_metrics_enabled = true
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
}
