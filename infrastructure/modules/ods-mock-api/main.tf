resource "aws_api_gateway_rest_api" "ods_mock" {
  name        = var.api_gateway_name
  description = var.api_gateway_description

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name = var.api_gateway_name
  }

  lifecycle {
    create_before_destroy = true
  }
}

locals {
  vtl_template = file("${path.module}/templates/ods_mock_basic.vtl")
}

resource "aws_api_gateway_request_validator" "validator" {
  rest_api_id                 = aws_api_gateway_rest_api.ods_mock.id
  name                        = "${var.api_gateway_name}-validator"
  validate_request_body       = true
  validate_request_parameters = true
}

resource "aws_api_gateway_resource" "organisation_data_terminology_api" {
  rest_api_id = aws_api_gateway_rest_api.ods_mock.id
  parent_id   = aws_api_gateway_rest_api.ods_mock.root_resource_id
  path_part   = "organisation-data-terminology-api"
}

resource "aws_api_gateway_resource" "fhir" {
  rest_api_id = aws_api_gateway_rest_api.ods_mock.id
  parent_id   = aws_api_gateway_resource.organisation_data_terminology_api.id
  path_part   = "fhir"
}

resource "aws_api_gateway_resource" "organization" {
  rest_api_id = aws_api_gateway_rest_api.ods_mock.id
  parent_id   = aws_api_gateway_resource.fhir.id
  path_part   = "Organization"
}

resource "aws_api_gateway_method" "organization_get" {
  rest_api_id          = aws_api_gateway_rest_api.ods_mock.id
  resource_id          = aws_api_gateway_resource.organization.id
  http_method          = "GET"
  authorization        = "NONE"
  api_key_required     = true
  request_validator_id = aws_api_gateway_request_validator.validator.id

  request_parameters = {
    "method.request.querystring._lastUpdated" = false
  }
}

resource "aws_api_gateway_integration" "organization_get_mock" {
  rest_api_id = aws_api_gateway_rest_api.ods_mock.id
  resource_id = aws_api_gateway_resource.organization.id
  http_method = aws_api_gateway_method.organization_get.http_method

  type = "MOCK"

  request_templates = {
    "application/json" = local.vtl_template
  }
}

resource "aws_api_gateway_method_response" "organization_get_200" {
  rest_api_id = aws_api_gateway_rest_api.ods_mock.id
  resource_id = aws_api_gateway_resource.organization.id
  http_method = aws_api_gateway_method.organization_get.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Content-Type" = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_method_response" "organization_get_401" {
  rest_api_id = aws_api_gateway_rest_api.ods_mock.id
  resource_id = aws_api_gateway_resource.organization.id
  http_method = aws_api_gateway_method.organization_get.http_method
  status_code = "401"

  response_parameters = {
    "method.response.header.Content-Type" = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_method_response" "organization_get_500" {
  rest_api_id = aws_api_gateway_rest_api.ods_mock.id
  resource_id = aws_api_gateway_resource.organization.id
  http_method = aws_api_gateway_method.organization_get.http_method
  status_code = "500"

  response_parameters = {
    "method.response.header.Content-Type" = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "organization_get_200" {
  rest_api_id = aws_api_gateway_rest_api.ods_mock.id
  resource_id = aws_api_gateway_resource.organization.id
  http_method = aws_api_gateway_method.organization_get.http_method
  status_code = aws_api_gateway_method_response.organization_get_200.status_code

  response_parameters = {
    "method.response.header.Content-Type" = "'application/fhir+json'"
  }

  response_templates = {
    "application/json" = "$input.json('$')"
  }

  depends_on = [aws_api_gateway_integration.organization_get_mock]
}

resource "aws_api_gateway_integration_response" "organization_get_401" {
  rest_api_id       = aws_api_gateway_rest_api.ods_mock.id
  resource_id       = aws_api_gateway_resource.organization.id
  http_method       = aws_api_gateway_method.organization_get.http_method
  status_code       = aws_api_gateway_method_response.organization_get_401.status_code
  selection_pattern = "401"

  response_parameters = {
    "method.response.header.Content-Type" = "'application/fhir+json'"
  }

  response_templates = {
    "application/json" = "$input.json('$')"
  }

  depends_on = [aws_api_gateway_integration.organization_get_mock]
}

resource "aws_api_gateway_integration_response" "organization_get_500" {
  rest_api_id       = aws_api_gateway_rest_api.ods_mock.id
  resource_id       = aws_api_gateway_resource.organization.id
  http_method       = aws_api_gateway_method.organization_get.http_method
  status_code       = aws_api_gateway_method_response.organization_get_500.status_code
  selection_pattern = "500"

  response_parameters = {
    "method.response.header.Content-Type" = "'application/fhir+json'"
  }

  response_templates = {
    "application/json" = "$input.json('$')"
  }

  depends_on = [aws_api_gateway_integration.organization_get_mock]
}

resource "aws_api_gateway_deployment" "ods_mock" {
  rest_api_id = aws_api_gateway_rest_api.ods_mock.id

  depends_on = [
    aws_api_gateway_integration_response.organization_get_200,
    aws_api_gateway_integration_response.organization_get_401,
    aws_api_gateway_integration_response.organization_get_500,
  ]

  triggers = {
    redeployment = sha256(local.vtl_template)
    timestamp    = timestamp()
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "ods_mock" {
  # checkov:skip=CKV2_AWS_29: Mock API for dev testing, WAF protection not required
  # checkov:skip=CKV2_AWS_51: Using API key authentication instead of client certificates for mock API simplicity
  # checkov:skip=CKV2_AWS_4: False positive, we are configuring custom logging
  deployment_id = aws_api_gateway_deployment.ods_mock.id
  rest_api_id   = aws_api_gateway_rest_api.ods_mock.id
  stage_name    = "dev"

  xray_tracing_enabled = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_log_group.arn
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

  cache_cluster_enabled = true
  cache_cluster_size    = "0.5"

  tags = {
    Name        = "${var.api_gateway_name}-dev"
    Environment = var.environment
  }
}

resource "aws_api_gateway_method_settings" "ods_mock" {
  rest_api_id = aws_api_gateway_rest_api.ods_mock.id
  stage_name  = aws_api_gateway_stage.ods_mock.stage_name
  method_path = "*/*"

  settings {
    logging_level        = "INFO"
    caching_enabled      = true
    cache_ttl_in_seconds = 300
    cache_data_encrypted = true
  }
}

resource "aws_cloudwatch_log_group" "api_gateway_log_group" {
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  # checkov:skip=CKV_AWS_338: Justification: Non-production do not require long term log retention.
  name              = "/aws/api-gateway/${var.api_gateway_name}"
  retention_in_days = var.api_gateway_log_group_retention_days
  log_group_class   = var.api_gateway_log_group_class
}

resource "aws_api_gateway_api_key" "ods_mock" {
  name        = "${var.api_gateway_name}-key"
  description = "API key for ODS mock API"
  tags = {
    Name = "${var.api_gateway_name}-key"
  }
}

resource "aws_api_gateway_usage_plan" "ods_mock" {
  name        = "${var.api_gateway_name}-plan"
  description = "Usage plan for ODS mock API"
  tags = {
    Name = "${var.api_gateway_name}-plan"
  }

  api_stages {
    api_id = aws_api_gateway_rest_api.ods_mock.id
    stage  = aws_api_gateway_stage.ods_mock.stage_name
  }

  throttle_settings {
    burst_limit = var.throttle_burst_limit
    rate_limit  = var.throttle_rate_limit
  }

  quota_settings {
    limit  = var.quota_limit
    period = "DAY"
  }
}

resource "aws_api_gateway_usage_plan_key" "ods_mock" {
  key_id        = aws_api_gateway_api_key.ods_mock.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.ods_mock.id
}
