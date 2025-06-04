resource "aws_api_gateway_resource" "search_resource" {
  parent_id   = module.search_rest_api.root_resource_id
  path_part   = "search"
  rest_api_id = module.search_rest_api.rest_api_id
}

resource "aws_api_gateway_method" "search_get" {
  authorization = "NONE"
  http_method   = "GET"
  resource_id   = aws_api_gateway_resource.search_resource.id
  rest_api_id   = module.search_rest_api.rest_api_id

  depends_on = [
    aws_api_gateway_resource.search_resource
  ]
}
