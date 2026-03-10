# Resource names
s3_bucket_name = "dos-search-s3"

# Organization Lambda
organization_name           = "organization-lambda"
organization_lambda_handler = "src.organization.handler.lambda_handler"

# Health Check Lambda
health_check_name           = "health-check-lambda"
health_check_lambda_handler = "src.health_check.handler.lambda_handler"

# Healthcare Service Lambda
healthcare_service_lambda_name = "healthcare-service-lambda"

#Lambda
lambda_runtime     = "python3.12"
lambda_timeout     = 900
lambda_memory_size = 512

# API Gateway throttling defaults (overridable per-environment)
api_gateway_throttling_rate_limit  = 200
api_gateway_throttling_burst_limit = 450
