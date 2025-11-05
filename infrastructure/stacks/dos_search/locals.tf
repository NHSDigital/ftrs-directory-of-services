// Shared locals for API Gateway FHIR OperationOutcome responses
locals {
  fhir_content_type_header = {
    "gatewayresponse.header.Content-Type" = "'application/fhir+json'"
  }

  fhir_templates = {
    not_found = <<EOT
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "not-found",
      "diagnostics": "No such endpoint",
      "details": {
        "coding": [
          {
            "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-SpineErrorOrWarningCode",
            "version": "1.0.0",
            "code": "NOT_FOUND",
            "display": "Not Found"
          }
        ]
      }
    }
  ]
}
EOT

    access_denied = <<EOT
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "security",
      "diagnostics": "Invalid or missing client authentication",
      "details": {
        "coding": [
          {
            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
            "version": "1",
            "code": "UNAUTHORIZED",
            "display": "Unauthorized"
          }
        ]
      }
    }
  ]
}
EOT

    internal_error = <<EOT
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "fatal",
      "code": "exception",
      "details": {
        "coding": [
          {
            "system": "http://hl7.org/fhir/issue-type",
            "code": "exception",
            "display": "Exception"
          }
        ]
      },
      "diagnostics": "Internal server error"
    }
  ]
}
EOT

    bad_request = <<EOT
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "invalid",
      "details": {
        "coding": [
          {
            "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-SpineErrorOrWarningCode",
            "version": "1.0.0",
            "code": "INVALID_SEARCH_DATA",
            "display": "Invalid search data"
          }
        ]
      },
      "diagnostics": "Bad request"
    }
  ]
}
EOT

    throttled = <<EOT
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "throttled",
      "details": {
        "coding": [
          {
            "system": "http://hl7.org/fhir/issue-type",
            "code": "throttled",
            "display": "Throttled"
          }
        ]
      },
      "diagnostics": "Too many requests"
    }
  ]
}
EOT

    timeout = <<EOT
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "fatal",
      "code": "timeout",
      "details": {
        "coding": [
          {
            "system": "http://hl7.org/fhir/issue-type",
            "code": "timeout",
            "display": "Timeout"
          }
        ]
      },
      "diagnostics": "Gateway timeout"
    }
  ]
}
EOT
  }

  # Define all gateway-level responses in one place
  gateway_responses = {
    resource_not_found = {
      response_type = "RESOURCE_NOT_FOUND"
      status_code   = "404"
      template      = local.fhir_templates.not_found
    }
    missing_authentication_token = {
      response_type = "MISSING_AUTHENTICATION_TOKEN"
      status_code   = "404"
      template      = local.fhir_templates.not_found
    }
    access_denied = {
      response_type = "ACCESS_DENIED"
      status_code   = "403"
      template      = local.fhir_templates.access_denied
    }

    # 400 targeted
    bad_request_parameters = {
      response_type = "BAD_REQUEST_PARAMETERS"
      status_code   = "400"
      template      = local.fhir_templates.bad_request
    }
    bad_request_body = {
      response_type = "BAD_REQUEST_BODY"
      status_code   = "400"
      template      = local.fhir_templates.bad_request
    }
    default_4xx = {
      response_type = "DEFAULT_4XX"
      status_code   = "400"
      template      = local.fhir_templates.bad_request
    }

    # 429 targeted
    throttled = {
      response_type = "THROTTLED"
      status_code   = "429"
      template      = local.fhir_templates.throttled
    }

    # 504 targeted
    integration_timeout = {
      response_type = "INTEGRATION_TIMEOUT"
      status_code   = "504"
      template      = local.fhir_templates.timeout
    }

    # 5xx default
    default_5xx = {
      response_type = "DEFAULT_5XX"
      status_code   = "500"
      template      = local.fhir_templates.internal_error
    }
  }

  # Deterministic projection of gateway responses used for API Gateway redeployment hashing
  gateway_responses_projection = [
    for k in keys(local.gateway_responses) : {
      key           = k
      response_type = local.gateway_responses[k].response_type
      status_code   = local.gateway_responses[k].status_code
      template      = local.gateway_responses[k].template
    }
  ]
}
