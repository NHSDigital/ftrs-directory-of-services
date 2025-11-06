variable "dos_search_service_name" {
  description = "The name of the gp search service"
}

variable "s3_bucket_name" {
  description = "The name of the gp search bucket"
}

variable "lambda_name" {
  description = "The name of the gp search lambda"
}

variable "health_check_lambda_name" {
  description = "The name of the health check lambda for gp search"
}

variable "lambda_runtime" {
  description = "The runtime environment for the lambda function"
}

variable "lambda_memory_size" {
  description = "The memory size of the lambda function"
  type        = number
}

variable "lambda_timeout" {
  description = "The connection timeout of the lambda function"
  type        = number
}

variable "application_tag" {
  description = "The version or tag of the gp search application"
  type        = string
  default     = "latest"
}

#####################################################

# API Gateway

variable "api_gateway_name" {
  description = "The name of the API Gateway"
  default     = "default"
}

variable "api_gateway_description" {
  description = "The description of the API Gateway"
  default     = "DoS Search API"
}

variable "api_gateway_log_group_class" {
  description = "The logging group class of the API Gateway log group"
  default     = "STANDARD"
}

variable "api_gateway_log_group_retention_days" {
  description = "The period of time in days to retain logs for the API Gateway log group"
  default     = "7"
}

variable "api_gateway_xray_tracing" {
  description = "Flag to enable or disable xray tracing at the API Gateway"
  default     = true
}

variable "api_gateway_logging_level" {
  description = "The level of logging"
  default     = "INFO"
}

variable "api_gateway_method_cache_enabled" {
  description = "Configure caching at the method level"
  default     = true
}

variable "api_gateway_method_metrics_enabled" {
  description = "Configure gathering metrics at end point level"
  default     = true
}

variable "api_gateway_tls_security_policy" {
  description = "The TLS security policy of the API Gateway when negotiating SSL handshakes"
  default     = "TLS_1_2"
}

variable "lambda_cloudwatch_logs_retention_days" {
  description = "Number of days to retain CloudWatch logs for the main search Lambda"
  type        = number
  default     = 7
}

variable "health_check_lambda_cloudwatch_logs_retention_days" {
  description = "Number of days to retain CloudWatch logs for the health check Lambda"
  type        = number
  default     = 7
}

variable "api_gateway_throttling_rate_limit" {
  description = "Throttling rate limit for the API Gateway (requests per second)"
  type        = number
}

variable "api_gateway_throttling_burst_limit" {
  description = "Throttling burst limit for the API Gateway"
  type        = number
}

# FHIR error response header mapping (Content-Type)
variable "fhir_content_type_header" {
  description = "API Gateway response header mappings for FHIR responses"
  type        = map(string)
  default = {
    "gatewayresponse.header.Content-Type" = "'application/fhir+json'"
  }
}

# Gateway response definitions for API Gateway
variable "gateway_responses" {
  description = "Map of API Gateway gateway_responses with response_type, status_code, and FHIR template"
  type = map(object({
    response_type = string
    status_code   = string
    template      = string
  }))
  default = {
    resource_not_found = {
      response_type = "RESOURCE_NOT_FOUND"
      status_code   = "404"
      template      = <<EOT
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
    }
    missing_authentication_token = {
      response_type = "MISSING_AUTHENTICATION_TOKEN"
      status_code   = "404"
      template      = <<EOT
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
    }
    access_denied = {
      response_type = "ACCESS_DENIED"
      status_code   = "403"
      template      = <<EOT
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
    }
    bad_request_parameters = {
      response_type = "BAD_REQUEST_PARAMETERS"
      status_code   = "400"
      template      = <<EOT
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
    }
    bad_request_body = {
      response_type = "BAD_REQUEST_BODY"
      status_code   = "400"
      template      = <<EOT
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
    }
    default_4xx = {
      response_type = "DEFAULT_4XX"
      status_code   = "400"
      template      = <<EOT
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
    }
    throttled = {
      response_type = "THROTTLED"
      status_code   = "429"
      template      = <<EOT
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
    }
    integration_timeout = {
      response_type = "INTEGRATION_TIMEOUT"
      status_code   = "504"
      template      = <<EOT
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
    default_5xx = {
      response_type = "DEFAULT_5XX"
      status_code   = "500"
      template      = <<EOT
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
    }
  }
}
