# Healthcare Service Resource
resource "aws_api_gateway_resource" "healthcare_service" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "healthcare-service"
}

# Healthcare Service Proxy Resource (for any sub-paths)
resource "aws_api_gateway_resource" "healthcare_service_proxy" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_resource.healthcare_service.id
  path_part   = "{proxy+}"
}

# ANY /healthcare-service/{proxy+}
resource "aws_api_gateway_method" "healthcare_service_proxy" {
  # checkov:skip=CKV_AWS_59: False positive; all the endpoints will be authenticated via mTLS
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.healthcare_service_proxy.id
  http_method   = "ANY"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validator.id
}

resource "aws_api_gateway_integration" "healthcare_service_proxy" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
  resource_id             = aws_api_gateway_resource.healthcare_service_proxy.id
  http_method             = aws_api_gateway_method.healthcare_service_proxy.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.healthcare_service_api_lambda.lambda_function_invoke_arn
}
