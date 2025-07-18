resource "aws_api_gateway_rest_api" "rest_api" {
  name                         = "${var.rest_api_name}${local.workspace_suffix}"
  disable_execute_api_endpoint = true
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

