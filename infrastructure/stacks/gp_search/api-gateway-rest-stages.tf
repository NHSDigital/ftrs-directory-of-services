resource "aws_api_gateway_stage" "default" {
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api-gateway.id
  stage_name    = "default"

  xray_tracing_enabled = true

  # access_log_settings {
  #   destination_arn = TBC
  #   format = jsonencode({
  #     context = {
  #       domainName              = "$context.domainName"
  #       integrationErrorMessage = "$context.integrationErrorMessage"
  #       protocol                = "$context.protocol"
  #       requestId               = "$context.requestId"
  #       requestTime             = "$context.requestTime"
  #       responseLength          = "$context.responseLength"
  #       routeKey                = "$context.routeKey"
  #       stage                   = "$context.stage"
  #       status                  = "$context.status"
  #       error = {
  #         message      = "$context.error.message"
  #         responseType = "$context.error.responseType"
  #       }
  #       identity = {
  #         sourceIP = "$context.identity.sourceIp"
  #       }
  #       integration = {
  #         error             = "$context.integration.error"
  #         integrationStatus = "$context.integration.integrationStatus"
  #       }
  #     }
  #   })
  # }

}

# JP - WAF ACL association goes here
# resource "aws_wafv2_web_acl_association" "waf_attachment_default" {
#   resource_arn = aws_api_gateway_stage.default.arn
#   web_acl_arn  = aws_wafv2_web_acl.example.arn
# }


