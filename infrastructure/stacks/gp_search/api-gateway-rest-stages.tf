resource "aws_api_gateway_stage" "default" {
  # checkov:skip=CKV2_AWS_29: DOSIS-2197 - Deploy and attach WAF
  # checkov:skip=CKV2_AWS_51: False positive, the API is secured by mTLS via DNS domain certificate
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api-gateway.id
  stage_name    = "default"

  cache_cluster_enabled = true

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

}

resource "aws_cloudwatch_log_group" "api_gateway_log_group" {
  # checkov:skip=CKV_AWS_158: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-404
  name              = "/aws/api-gateway/${local.resource_prefix}${local.workspace_suffix}"
  retention_in_days = var.api_gateway_log_group_retention_days
  log_group_class   = var.api_gateway_log_group_class
}

# JP - WAF ACL association goes here (DOSIS-2197)
# resource "aws_wafv2_web_acl_association" "waf_attachment_default" {
#   resource_arn = aws_api_gateway_stage.default.arn
#   web_acl_arn  = aws_wafv2_web_acl.example.arn
# }
