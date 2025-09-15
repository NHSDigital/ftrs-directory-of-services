gp_search_service_name = "ftrs-dos-gp-search"

# Resource names
s3_bucket_name           = "gp-search-s3"
lambda_name              = "gp-search-lambda"
health_check_lambda_name = "health-check-lambda"

#Lambda
lambda_runtime     = "python3.12"
lambda_timeout     = 900
lambda_memory_size = 512

# API Gateway
# The payload format version has to be 1.0 as this is the payload format that the
# current Lambda event handlers require. To move to 2.0 we'd need to use some different
# lambda libraries.
api_gateway_payload_format_version     = "1.0"
api_gateway_integration_timeout        = 20000
api_gateway_access_logs_retention_days = 7
