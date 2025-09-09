# resource "aws_apigatewayv2_route" "sandbox_org" {
#   count              = var.environment == "dev" ? 1 : 0
#   api_id             = module.api_gateway.api_id
#   route_key          = "GET /Organization"
#   target             = "integrations/${aws_apigatewayv2_integration.sandbox_org[count.index].id}"
# }

# resource "aws_apigatewayv2_integration" "sandbox_org" {
#   count                = var.environment == "dev" ? 1 : 0
#   api_id               = module.api_gateway.api_id
#   integration_type     = "MOCK"
#   integration_method   = "GET"
#   payload_format_version = "1.0"
# }

# resource "aws_apigatewayv2_route" "sandbox_org_proxy" {
#   count              = var.environment == "dev" ? 1 : 0
#   api_id             = module.api_gateway.api_id
#   route_key          = "ANY /Organization/{proxy+}"
#   target             = "integrations/${aws_apigatewayv2_integration.sandbox_org_proxy[count.index].id}"
# }

# resource "aws_apigatewayv2_integration" "sandbox_org_proxy" {
#   count                = var.environment == "dev" ? 1 : 0
#   api_id               = module.api_gateway.api_id
#   integration_type     = "MOCK"
#   payload_format_version = "1.0"
# }

module "api_gateway_sandbox" {
  count  = var.environment == "dev" ? 1 : 0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2.git?ref=5d1548624b39145ead043794ae5762abb9aadb27"

  name          = "${local.resource_prefix}-api-gateway${local.workspace_suffix}"
  protocol_type = "HTTP"
  # TODO: To be disabled after APIM, ETL and Dos Reader integration start using mTLS endpoint (SIA-647 & SIA-649 & TBC )
  # disable_execute_api_endpoint = true

  create_domain_name    = false
  create_domain_records = false

  # routes = var.environment == "sandbox" ? {
  routes = {
    "GET /Organization" = {
      integration = {
        integration_type = "MOCK"
      }
    }
    "ANY /Organization/{proxy+}" = {
      integration = {
        integration_type = "MOCK"
      }
    }
    "ANY /healthcare-service/{proxy+}" = {
      integration = {
        integration_type = "MOCK"
      }
    }
    "ANY /location/{proxy+}" = {
      integration = {
        integration_type = "MOCK"
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
    throttling_burst_limit   = var.api_gateway_throttling_burst_limit
    throttling_rate_limit    = var.api_gateway_throttling_rate_limit
  }
}
