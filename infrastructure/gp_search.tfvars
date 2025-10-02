gp_search_service_name = "ftrs-dos-gp-search"

# Resource names
lambda_name              = "gp-search-lambda"
health_check_lambda_name = "health-check-lambda"

#Lambda
lambda_runtime     = "python3.12"
lambda_timeout     = 900
lambda_memory_size = 512

# API Gateway
api_gateway_payload_format_version     = "2.0"
api_gateway_integration_timeout        = 10000
api_gateway_access_logs_retention_days = 7
