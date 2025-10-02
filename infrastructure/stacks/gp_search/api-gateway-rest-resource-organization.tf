resource "aws_api_gateway_resource" "organization" {
  rest_api_id = aws_api_gateway_rest_api.api-gateway.id
  parent_id   = aws_api_gateway_rest_api.api-gateway.root_resource_id
  path_part   = "Organization"
}

# Method request / response and integration request / response

resource "aws_api_gateway_method" "organization" {
  # checkov:skip=CKV_AWS_59: False positive; all the endpoints will be authenticated via mTLS
  rest_api_id   = aws_api_gateway_rest_api.api-gateway.id
  resource_id   = aws_api_gateway_resource.organization.id
  http_method   = "GET"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validator.id
}

resource "aws_api_gateway_integration" "organization" {
  rest_api_id             = aws_api_gateway_rest_api.api-gateway.id
  resource_id             = aws_api_gateway_resource.organization.id
  http_method             = aws_api_gateway_method.organization.http_method
  integration_http_method = "GET"
  type                    = "AWS"
  uri                     = module.lambda.lambda_function_invoke_arn
}

resource "aws_api_gateway_method_response" "organization" {
  rest_api_id = aws_api_gateway_rest_api.api-gateway.id
  resource_id = aws_api_gateway_resource.organization.id
  http_method = aws_api_gateway_method.organization.http_method
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "organization" {
  rest_api_id = aws_api_gateway_rest_api.api-gateway.id
  resource_id = aws_api_gateway_resource.organization.id
  http_method = aws_api_gateway_method.organization.http_method
  status_code = aws_api_gateway_method_response.organization.status_code

  depends_on = [
    aws_api_gateway_method.organization,
    aws_api_gateway_integration.organization
  ]
}
