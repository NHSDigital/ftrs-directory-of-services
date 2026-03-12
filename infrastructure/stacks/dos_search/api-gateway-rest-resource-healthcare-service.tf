resource "aws_api_gateway_resource" "healthcare_service" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "HealthcareService"
}

resource "aws_api_gateway_method" "healthcare_service" {
  # checkov:skip=CKV_AWS_59: False positive; all the endpoints will be authenticated via mTLS
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.healthcare_service.id
  http_method   = "GET"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validator.id
}

# API Gateway Integration for GET /HealthcareService
resource "aws_api_gateway_integration" "healthcare_service" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
  resource_id             = aws_api_gateway_resource.healthcare_service.id
  http_method             = aws_api_gateway_method.healthcare_service.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.healthcare_service_lambda.lambda_function_invoke_arn
}
