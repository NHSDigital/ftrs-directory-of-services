locals {
  account_id        = data.aws_caller_identity.current.id
  workspace_suffix  = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  artefacts_bucket  = "${var.repo_name}-mgmt-${var.artefacts_bucket_name}"
  resource_prefix   = "${var.project}-${var.environment}-${var.stack_name}"
  account_prefix    = "${var.repo_name}-${var.environment}"
  root_domain_name  = "${var.environment}.${var.root_domain_name}"
  s3_logging_bucket = "${local.account_prefix}-${var.s3_logging_bucket_name}"

  # Deploy certain resources (e.g., databases, backup SSM) only in default Terraform workspace.
  is_primary_environment = terraform.workspace == "default"
  rds_environments       = var.environment == "dev" || var.environment == "test" || var.environment == "int"

  dynamodb_tables = {
    for table_name in var.dynamodb_table_names :
    table_name => {
      arn = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.project}-${var.environment}-database-${table_name}${local.workspace_suffix}"
    }
  }

  gp_search_organisation_table_arn = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.project}-${var.environment}-database-${var.gp_search_organisation_table_name}"

  domain_cross_account_role = "${var.repo_name}-mgmt-domain-name-cross-account-access"

  env_domain_name = "${var.environment}.${var.root_domain_name}"

  s3_trust_store_bucket_name = "${local.account_prefix}-${var.s3_trust_store_bucket_name}"

  trust_store_file_path = "${var.environment}/truststore.pem"

  env_sso_roles = [
    for role in var.sso_roles : "arn:aws:iam::${local.account_id}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/${role}"
  ]

  # crud_api_gateway = var.environment == "dev" ? module.api_gateway_sandbox[0] : module.api_gateway_real[0]
  # Base route configurations
  # base_routes = {
  #   "GET /Organization" = {
  #     # No authorization_type for this route as per original
  #   }
  #   "ANY /Organization/{proxy+}" = {
  #     # No authorization_type for this route as per original
  #   }
  #   "ANY /healthcare-service/{proxy+}" = {
  #     authorization_type = var.api_gateway_authorization_type
  #   }
  #   "ANY /location/{proxy+}" = {
  #     authorization_type = var.api_gateway_authorization_type
  #   }
  # }

  # # Lambda integrations (for staging/prod)
  # lambda_integrations = {
  #   "GET /Organization" = {
  #     integration_type       = "AWS_PROXY"
  #     uri                    = module.organisation_api_lambda.lambda_function_arn
  #     payload_format_version = var.api_gateway_payload_format_version
  #     timeout_milliseconds   = var.api_gateway_integration_timeout
  #   }
  #   "ANY /Organization/{proxy+}" = {
  #     integration_type       = "AWS_PROXY"
  #     uri                    = module.organisation_api_lambda.lambda_function_arn
  #     payload_format_version = var.api_gateway_payload_format_version
  #     timeout_milliseconds   = var.api_gateway_integration_timeout
  #   }
  #   "ANY /healthcare-service/{proxy+}" = {
  #     integration_type       = "AWS_PROXY"
  #     uri                    = module.healthcare_service_api_lambda.lambda_function_arn
  #     payload_format_version = var.api_gateway_payload_format_version
  #     timeout_milliseconds   = var.api_gateway_integration_timeout
  #   }
  #   "ANY /location/{proxy+}" = {
  #     integration_type       = "AWS_PROXY"
  #     uri                    = module.location_api_lambda.lambda_function_arn
  #     payload_format_version = var.api_gateway_payload_format_version
  #     timeout_milliseconds   = var.api_gateway_integration_timeout
  #   }
  # }

  # # Mock integrations (for sandbox)
  # mock_integrations = {
  #   "GET /Organization" = {
  #     integration_type = "MOCK"
  #     request_templates = {
  #       "application/json" = "{\"statusCode\": 200}"
  #     }
  #     # Response template for dynamic ODS code handling
  #     templates = {
  #       "application/json" = <<-EOT
  #         #set($inputRoot = $input.path('$'))
  #         #set($queryParams = $input.params().querystring)
  #         #set($identifier = $queryParams.get('identifier'))

  #         #if($identifier && $identifier.startsWith('odsOrganisationCode|'))
  #           #set($odsCode = $identifier.substring(18))
  #           #set($orgData = {
  #             "C88006": {
  #               "id": "c6016de0-7ce0-5320-9496-1d13046ad46d",
  #               "name": "Dr Margaret Mckenna And Partners Norfolk Park",
  #               "type": "GP Practice",
  #               "display": "GP Practice",
  #               "active": true
  #             }
  #           })

  #           #if($orgData.containsKey($odsCode))
  #             #set($data = $orgData.get($odsCode))
  #             {
  #               "resourceType": "Bundle",
  #               "type": "searchset",
  #               "total": 1,
  #               "entry": [
  #                 {
  #                   "resource": {
  #                     "resourceType": "Organization",
  #                     "id": "$data.id",
  #                     "meta": {
  #                       "profile": [
  #                         "https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"
  #                       ]
  #                     },
  #                     "identifier": [
  #                       {
  #                         "use": "official",
  #                         "system": "https://fhir.nhs.uk/Id/ods-organization-code",
  #                         "value": "$odsCode"
  #                       }
  #                     ],
  #                     "active": $data.active,
  #                     "type": [
  #                       {
  #                         "coding": [
  #                           {
  #                             "system": "https://fhir.nhs.uk/CodeSystem/UKCore-OrganizationType",
  #                             "code": "$data.type",
  #                             "display": "$data.display"
  #                           }
  #                         ],
  #                         "text": "$data.type"
  #                       }
  #                     ],
  #                     "name": "$data.name",
  #                     "telecom": []
  #                   }
  #                 }
  #               ]
  #             }
  #           #else
  #             {
  #               "resourceType": "Bundle",
  #               "type": "searchset",
  #               "total": 0,
  #               "entry": []
  #             }
  #           #end
  #         #else
  #           {
  #             "resourceType": "Bundle",
  #             "type": "searchset",
  #             "total": 0,
  #             "entry": []
  #           }
  #         #end
  #       EOT
  #     }
  #   }
  #   "ANY /Organization/{proxy+}" = {
  #     integration_type = "MOCK"
  #     request_templates = {
  #       "application/json" = "{\"statusCode\": 200}"
  #     }
  #   }
  #   "ANY /healthcare-service/{proxy+}" = {
  #     integration_type = "MOCK"
  #     request_templates = {
  #       "application/json" = "{\"statusCode\": 200}"
  #     }
  #   }
  #   "ANY /location/{proxy+}" = {
  #     integration_type = "MOCK"
  #     request_templates = {
  #       "application/json" = "{\"statusCode\": 200}"
  #     }
  #   }
  # }

  # # Combined routes - choose integration based on environment
  # routes = { for route_key, base_config in local.base_routes :
  #   route_key => merge(base_config, {
  #     integration = var.environment == "dev" ? local.mock_integrations[route_key] : local.lambda_integrations[route_key]
  #   })
  # }
}
