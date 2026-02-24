# Organization Resource
resource "aws_api_gateway_resource" "organization" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "Organization"
}

# GET /Organization
resource "aws_api_gateway_method" "organization_get" {
  # checkov:skip=CKV_AWS_59: False positive; all the endpoints will be authenticated via mTLS
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.organization.id
  http_method   = "GET"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validator.id

  request_parameters = {
    "method.request.querystring.identifier" = true
  }

}

resource "aws_api_gateway_integration" "organization_get" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
  resource_id             = aws_api_gateway_resource.organization.id
  http_method             = aws_api_gateway_method.organization_get.http_method
  integration_http_method = "GET"
  type                    = "AWS_PROXY"
  uri                     = module.organisation_api_lambda.lambda_function_invoke_arn

  request_parameters = {
    "integration.request.querystring.identifier" = "method.request.querystring.identifier"
  }
}

# POST /Organization
resource "aws_api_gateway_method" "organization_post" {
  # checkov:skip=CKV_AWS_59: False positive; all the endpoints will be authenticated via mTLS
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.organization.id
  http_method   = "POST"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validator.id
}

resource "aws_api_gateway_integration" "organization_post" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
  resource_id             = aws_api_gateway_resource.organization.id
  http_method             = aws_api_gateway_method.organization_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.organisation_api_lambda.lambda_function_invoke_arn
}

# PUT /Organization
resource "aws_api_gateway_method" "organization_put" {
  # checkov:skip=CKV_AWS_59: False positive; all the endpoints will be authenticated via mTLS
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.organization.id
  http_method   = "PUT"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validator.id
}

resource "aws_api_gateway_integration" "organization_put" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
  resource_id             = aws_api_gateway_resource.organization.id
  http_method             = aws_api_gateway_method.organization_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.organisation_api_lambda.lambda_function_invoke_arn
}

# Organization Proxy Resource (for any sub-paths)
resource "aws_api_gateway_resource" "organization_proxy" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_resource.organization.id
  path_part   = "{proxy+}"
}

# ANY /Organization/{proxy+}
resource "aws_api_gateway_method" "organization_proxy" {
  # checkov:skip=CKV_AWS_59: False positive; all the endpoints will be authenticated via mTLS
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.organization_proxy.id
  http_method   = "ANY"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validator.id
}

resource "aws_api_gateway_integration" "organization_proxy" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
  resource_id             = aws_api_gateway_resource.organization_proxy.id
  http_method             = aws_api_gateway_method.organization_proxy.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.organisation_api_lambda.lambda_function_invoke_arn
}
