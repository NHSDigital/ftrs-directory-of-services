module "api_gateway" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2.git?ref=5d1548624b39145ead043794ae5762abb9aadb27"

  name          = "${local.resource_prefix}-api-gateway${local.workspace_suffix}"
  protocol_type = "HTTP"
  # TODO: To be disabled after APIM, ETL and Dos Reader integration start using mTLS endpoint (SIA-647 & SIA-649 & TBC )
  # disable_execute_api_endpoint = true

  create_domain_name    = false
  create_domain_records = false

  # TODO: FDOS-370 - Setup to use mTLS or API Keys
  routes = {
    "ANY /Organization/{proxy+}" = {
      integration = {
        uri                    = module.organisation_api_lambda.lambda_function_arn
        payload_format_version = var.api_gateway_payload_format_version
        timeout_milliseconds   = var.api_gateway_integration_timeout
      }
    }

    "ANY /healthcare-service/{proxy+}" = {
      authorization_type = var.api_gateway_authorization_type
      integration = {
        uri                    = module.healthcare_service_api_lambda.lambda_function_arn
        payload_format_version = var.api_gateway_payload_format_version
        timeout_milliseconds   = var.api_gateway_integration_timeout
      }
    }

    "ANY /location/{proxy+}" = {
      authorization_type = var.api_gateway_authorization_type
      integration = {
        uri                    = module.location_api_lambda.lambda_function_arn
        payload_format_version = var.api_gateway_payload_format_version
        timeout_milliseconds   = var.api_gateway_integration_timeout
      }
    }
  }

  stage_access_log_settings = {
    create_log_group            = true
    log_group_retention_in_days = var.api_gateway_access_log_retention_days
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
    throttling_burst_limit   = var.api_gateway_throttling_burst_limit
    throttling_rate_limit    = var.api_gateway_throttling_rate_limit
  }
}

resource "aws_ssm_parameter" "crud_api_endpoint" {
  name        = "/${local.resource_prefix}${local.workspace_suffix}/endpoint"
  description = "The endpoint URL for the CRUD API Gateway"
  type        = "String"
  value       = module.api_gateway.api_endpoint
}

# may need to change to APIM key, need to load with actual value
resource "aws_ssm_parameter" "crud_api_key" {
  name        = "/${local.resource_prefix}${local.workspace_suffix}/crud_api_key"
  description = "API Key for CRUD API Gateway"
  type        = "SecureString"
  value       = "your-api-key-value" # Replace with your actual key or use a variable
}
