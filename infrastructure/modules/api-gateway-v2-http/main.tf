# This module will:
#    - Create an HTTP API Gateway v2 with a specified name and description
#    - Create domain names for the API Gateway (if create_domain_name is set to true). Note that if specifying domain names, the default
#      execute API endpoint will be disabled, so all routing will need to go through the R53 DNS routes
#    - Create domain records (A (IP4) and AAAA (IP6) records) in a specified hosted zone (if create_domain_records is set to true)
#    - The module supports TLSv1.2 and TLSv1.3. This cannot be configured in this version (5.3.1)
#    - The module will not create an SSL certificate for the domain as we are sharing a certificate across domains, but the Gateway will
#      need to be given the ARN of the shared certificate via the domain_certificate_arn variable
#    - The module will configure mTLS authentication. Therefore the URI to the mTLS truststore will need to be provided via the mtls_truststore_uri
#      variable
#    - Routes are passed in as a map of routes (see module documentation) via the routes variable
#    - All routes will have detailed metrics enabled
#    - All routes will have logging enabled to Cloudwatch

module "api_gateway" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2.git?ref=c62c315eeab078913c51d7d6a5eb722f4c1e82f5"
  # version = 5.3.1
  # https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest
  name          = var.name
  description   = var.description
  protocol_type = "HTTP"

  create_domain_name = var.create_domain_name
  domain_name        = var.domain_name

  create_domain_records = var.create_domain_records
  hosted_zone_name      = var.hosted_zone_name

  create_certificate          = false
  domain_name_certificate_arn = var.domain_certificate_arn

  mutual_tls_authentication = {
    truststore_uri = var.mtls_truststore_uri
  }

  # JP - At some point we may want to implement CORS
  # cors_configuration = {
  #   allow_headers = ["content-type", "x-amz-date", "authorization", "x-api-key", "x-amz-security-token", "x-amz-user-agent"]
  #   allow_methods = ["*"]
  #   allow_origins = ["*"]
  # }

  routes = var.routes

  stage_default_route_settings = {
    detailed_metrics_enabled = true
  }

  stage_access_log_settings = {
    create_log_group = true
    # log_group_retention_in_days and log_group_name removed so stacks supply them explicitly
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
