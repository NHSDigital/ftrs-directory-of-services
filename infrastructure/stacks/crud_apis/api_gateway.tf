module "api_gateway" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2.git?ref=5d1548624b39145ead043794ae5762abb9aadb27"

  name          = "${local.resource_prefix}-api-gateway${local.workspace_suffix}"
  protocol_type = "HTTP"

  create_domain_name    = false
  create_domain_records = false


  routes = {
    "ANY /organisation/{proxy+}" = {
      # TODO: Setup to use mTLS or API Keys
      authorization_type = "AWS_IAM"
      integration = {
        uri                    = module.organisation_api_lambda.lambda_function_arn
        payload_format_version = "2.0"
        timeout_milliseconds   = 10000
      }
    }

    "ANY /healthcare-service/{proxy+}" = {
      authorization_type = "AWS_IAM"
      integration = {
        uri                    = module.healthcare_service_api_lambda.lambda_function_arn
        payload_format_version = "2.0"
        timeout_milliseconds   = 10000
      }
    }

    # "ANY /location/{proxy+}" = {
    #   authorization_type = "AWS_IAM"
    #   integration = {
    #     uri                    = module.location_api_lambda.lambda_function_arn
    #     payload_format_version = "2.0"
    #     timeout_milliseconds   = 10000
    #   }
    # }
  }

  stage_access_log_settings = {
    create_log_group            = true
    log_group_retention_in_days = 7
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
    throttling_burst_limit   = 100
    throttling_rate_limit    = 10
  }
}

resource "aws_ssm_parameter" "crud_api_endpoint" {
  name        = "/${local.resource_prefix}${local.workspace_suffix}/endpoint"
  description = "The endpoint URL for the CRUD API Gateway"
  type        = "String"
  value       = module.api_gateway.api_endpoint
}
