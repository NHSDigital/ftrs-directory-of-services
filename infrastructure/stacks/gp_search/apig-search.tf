resource "aws_api_gateway_resource" "search_resource" {
  parent_id   = module.search_rest_api.root_resource_id
  path_part   = "Organization"
  rest_api_id = module.search_rest_api.rest_api_id
}

resource "aws_api_gateway_method" "search_get" {
  # checkov:skip=CKV_AWS_59: TODO https://nhsd-jira.digital.nhs.uk/browse/DOSIS-1840
  # checkov:skip=CKV2_AWS_53: TODO https://nhsd-jira.digital.nhs.uk/browse/DOSIS-1840
  authorization = "NONE"
  http_method   = "GET"
  resource_id   = aws_api_gateway_resource.search_resource.id
  rest_api_id   = module.search_rest_api.rest_api_id

  depends_on = [
    aws_api_gateway_resource.search_resource
  ]
}

module "search_integrations_get" {
  source               = "../../modules/api-gateway-integrations"
  aws_region           = var.aws_region
  account_id           = local.account_id
  rest_api_id          = module.search_rest_api.rest_api_id
  http_method          = aws_api_gateway_method.search_get.http_method
  lambda_function_name = "${local.resource_prefix}-${var.lambda_name}"
  gateway_resource_id  = aws_api_gateway_resource.search_resource.id

  depends_on = [
    aws_api_gateway_resource.search_resource,
    aws_api_gateway_method.search_get
  ]
}
