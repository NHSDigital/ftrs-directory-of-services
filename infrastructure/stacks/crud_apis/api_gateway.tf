module "api_gateway" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2.git?ref=5d1548624b39145ead043794ae5762abb9aadb27"

  name          = "${local.resource_prefix}-api-gateway${local.workspace_suffix}"
  protocol_type = "HTTP"
  # TODO: To be disabled after APIM, ETL and Dos Reader integration start using mTLS endpoint (SIA-647 & SIA-649 & TBC )
  # disable_execute_api_endpoint = true

  create_domain_name    = false
  create_domain_records = false

  # routes = var.environment == "dev" ? {
  routes = {
    "GET /Organization" = {
      integration = {
        integration_type = "MOCK"
        uri              = "http://example.com"
        request_templates = {
          "application/json" = "{\"statusCode\": 200}"
        }
        templates = {
          "application/json" = <<EOF
{
  "resourceType": "Organization",
  "id": "mock-org",
  "name": "Mock Organization",
  "telecom": [
    {
      "system": "phone",
      "value": "01234 567890"
    }
  ],
  "type": [
    {
      "text": "GP Practice"
    }
  ],
  "active": true
}
EOF
        }
        # payload_format_version = var.api_gateway_payload_format_version
        # timeout_milliseconds   = var.api_gateway_integration_timeout
      }
    }
    "ANY /Organization/{proxy+}" = {
      integration = {
        integration_type = "MOCK"
        uri              = "http://example.com"
        request_templates = {
          "application/json" = "{\"statusCode\": 200}"
        }
        templates = {
          "application/json" = <<EOF
{
  "resourceType": "Organization",
  "id": "mock-org",
  "name": "Mock Organization",
  "telecom": [
    {
      "system": "phone",
      "value": "01234 567890"
    }
  ],
  "type": [
    {
      "text": "GP Practice"
    }
  ],
  "active": true
}
EOF
        }
        # payload_format_version = var.api_gateway_payload_format_version
        # timeout_milliseconds   = var.api_gateway_integration_timeout
      }
    }
    "ANY /healthcare-service/{proxy+}" = {
      authorization_type = var.api_gateway_authorization_type
      integration = {
        integration_type = "MOCK"
        uri              = "http://example.com"
        request_templates = {
          "application/json" = "{\"statusCode\": 200}"
        }
        templates = {
          "application/json" = <<EOF
{
  "resourceType": "Organization",
  "id": "mock-org",
  "name": "Mock Organization",
  "telecom": [
    {
      "system": "phone",
      "value": "01234 567890"
    }
  ],
  "type": [
    {
      "text": "GP Practice"
    }
  ],
  "active": true
}
EOF
        }
        # payload_format_version = var.api_gateway_payload_format_version
        # timeout_milliseconds   = var.api_gateway_integration_timeout
      }
    }
    "ANY /location/{proxy+}" = {
      authorization_type = var.api_gateway_authorization_type
      integration = {
        integration_type = "MOCK"
        uri              = "http://example.com"
        request_templates = {
          "application/json" = "{\"statusCode\": 200}"
        }
        templates = {
          "application/json" = <<EOF
{
  "resourceType": "Organization",
  "id": "mock-org",
  "name": "Mock Organization",
  "telecom": [
    {
      "system": "phone",
      "value": "01234 567890"
    }
  ],
  "type": [
    {
      "text": "GP Practice"
    }
  ],
  "active": true
}
EOF
        }
        # payload_format_version = var.api_gateway_payload_format_version
        # timeout_milliseconds   = var.api_gateway_integration_timeout
      }
    }
  }
  #   } : {
  #   # routes = {
  #   "GET /Organization" = {
  #     integration = {
  #       integration_type       = "AWS_PROXY"
  #       uri                    = module.organisation_api_lambda.lambda_function_arn
  #       payload_format_version = var.api_gateway_payload_format_version
  #       timeout_milliseconds   = var.api_gateway_integration_timeout
  #     }
  #   }
  #   "ANY /Organization/{proxy+}" = {
  #     integration = {
  #       integration_type       = "AWS_PROXY"
  #       uri                    = module.organisation_api_lambda.lambda_function_arn
  #       payload_format_version = var.api_gateway_payload_format_version
  #       timeout_milliseconds   = var.api_gateway_integration_timeout
  #     }
  #   }
  #   "ANY /healthcare-service/{proxy+}" = {
  #     authorization_type = var.api_gateway_authorization_type
  #     integration = {
  #       integration_type       = "AWS_PROXY"
  #       uri                    = module.healthcare_service_api_lambda.lambda_function_arn
  #       payload_format_version = var.api_gateway_payload_format_version
  #       timeout_milliseconds   = var.api_gateway_integration_timeout
  #     }
  #   }
  #   "ANY /location/{proxy+}" = {
  #     authorization_type = var.api_gateway_authorization_type
  #     integration = {
  #       integration_type       = "AWS_PROXY"
  #       uri                    = module.location_api_lambda.lambda_function_arn
  #       payload_format_version = var.api_gateway_payload_format_version
  #       timeout_milliseconds   = var.api_gateway_integration_timeout
  #     }
  #   }
  # }

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


resource "aws_ssm_parameter" "crud_api_endpoint" {
  # checkov:skip=CKV2_AWS_34: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-402
  name        = "/${local.resource_prefix}${local.workspace_suffix}/endpoint"
  description = "The endpoint URL for the CRUD API Gateway"
  type        = "String"
  value       = module.api_gateway.api_endpoint
}

# resource "aws_apigatewayv2_integration" "organization_get" {
#   api_id                 = module.api_gateway.api_id
#   integration_uri       = "http://example.com" # Dummy URI for MOCK integration
#   integration_type       = "MOCK"
#   integration_method     = "GET"
#   payload_format_version = "1.0"
#   request_templates = {
#     "application/json" = "{\"statusCode\": 200}"
#   }
#   response_templates = {
#     "application/json" = <<EOF
# {
#   "resourceType": "Organization",
#   "id": "mock-org",
#   "name": "Mock Organization",
#   "telecom": [
#     {
#       "system": "phone",
#       "value": "01234 567890"
#     }
#   ],
#   "type": [
#     {
#       "text": "GP Practice"
#     }
#   ],
#   "active": true
# }
# EOF
#   }
# }
