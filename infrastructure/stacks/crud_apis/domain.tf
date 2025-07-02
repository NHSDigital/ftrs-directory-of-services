# data "aws_route53_zone" "main" {
#   zone_id = var.hosted_zone_id
# }

# resource "aws_apigatewayv2_domain_name" "api_domain" {
#   domain_name = "TEMP-${local.workspace_suffix}.${var.environment}.ftrs.cloud.nhs.uk"

#   domain_name_configuration {
#     # certificate_arn = var.mtls_certificate_arn != "" ? var.mtls_certificate_arn : aws_acm_certificate.api_cert[0].arn
#     certificate_arn = aws_acm_certificate.api_cert.arn
#     endpoint_type   = "REGIONAL"
#     security_policy = "TLS_1_2"
#   }

#   depends_on = [aws_acm_certificate_validation.api_cert]

#   tags = {
#     Name        = "${local.resource_prefix}-api-gateway${local.workspace_suffix}-domain"
#     Environment = var.environment
#   }
# }

# resource "aws_apigatewayv2_api_mapping" "api_mapping" {
#   api_id      = module.api_gateway.api_id
#   domain_name = aws_apigatewayv2_domain_name.api_domain.id
#   stage       = module.api_gateway.stage_id
# }

# resource "aws_route53_record" "api_record" {
#   zone_id = var.hosted_zone_id
#   name    = "TEMP-${local.workspace_suffix}.${var.environment}.ftrs.cloud.nhs.uk"
#   type    = "A"

#   alias {
#     name                   = aws_apigatewayv2_domain_name.api_domain.domain_name_configuration[0].target_domain_name
#     zone_id                = aws_apigatewayv2_domain_name.api_domain.domain_name_configuration[0].hosted_zone_id
#     evaluate_target_health = false
#   }
# }
