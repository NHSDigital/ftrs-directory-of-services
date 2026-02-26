# Location Resource
resource "aws_api_gateway_resource" "location" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "location"
}

# Location Proxy Resource (for any sub-paths)
resource "aws_api_gateway_resource" "location_proxy" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_resource.location.id
  path_part   = "{proxy+}"
}

# ANY /location/{proxy+}
resource "aws_api_gateway_method" "location_proxy" {
  # checkov:skip=CKV_AWS_59: False positive; all the endpoints will be authenticated via mTLS
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.location_proxy.id
  http_method   = "ANY"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validator.id
}

resource "aws_api_gateway_integration" "location_proxy" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
  resource_id             = aws_api_gateway_resource.location_proxy.id
  http_method             = aws_api_gateway_method.location_proxy.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.location_api_lambda.lambda_function_invoke_arn
}
