dos_search_service_name = "ftrs-dos-search"

# Resource names
s3_bucket_name           = "dos-search-s3"
lambda_name              = "ods-code-lambda"
health_check_lambda_name = "health-check-lambda"

#Lambda
lambda_runtime     = "python3.12"
lambda_timeout     = 900
lambda_memory_size = 512

# API Gateway throttling defaults (overridable per-environment)
api_gateway_throttling_rate_limit  = 150
api_gateway_throttling_burst_limit = 450
