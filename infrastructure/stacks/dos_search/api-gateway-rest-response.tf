locals {
  fhir_outcome_dir = "${path.module}/fhir_operation_outcomes"

  # Default FHIR OperationOutcome templates for API Gateway responses (loaded from files)
  gateway_responses_default = {
    resource_not_found = {
      response_type = "RESOURCE_NOT_FOUND"
      status_code   = "404"
      template      = file("${local.fhir_outcome_dir}/unsupported_service.json")
    }
    missing_authentication_token = {
      # Includes cases where unsupported API method or resource is called
      response_type = "MISSING_AUTHENTICATION_TOKEN"
      status_code   = "404"
      template      = file("${local.fhir_outcome_dir}/unsupported_service.json")
    }
    access_denied = {
      response_type = "ACCESS_DENIED"
      status_code   = "403"
      template      = file("${local.fhir_outcome_dir}/rec_forbidden.json")
    }
    unauthorized = {
      response_type = "UNAUTHORIZED"
      status_code   = "403"
      template      = file("${local.fhir_outcome_dir}/rec_forbidden.json")
    }
    default_4xx = {
      response_type = "DEFAULT_4XX"
      status_code   = "400"
      template      = file("${local.fhir_outcome_dir}/invalid_search_data.json")
    }
    throttled = {
      response_type = "THROTTLED"
      status_code   = "429"
      template      = file("${local.fhir_outcome_dir}/send_too_many_requests.json")
    }
    default_5xx = {
      response_type = "DEFAULT_5XX"
      status_code   = "500"
      template      = file("${local.fhir_outcome_dir}/fatal_exception.json")
    }
  }

  # Final gateway responses map: allow override via variable, else use defaults above
  gateway_responses = coalesce(var.gateway_responses, local.gateway_responses_default)
}

# Single, scalable definition for all configured gateway responses
resource "aws_api_gateway_gateway_response" "this" {
  for_each      = local.gateway_responses
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  response_type = each.value.response_type
  status_code   = each.value.status_code

  response_parameters = var.fhir_content_type_header

  response_templates = {
    "application/fhir+json" = each.value.template
  }
}
