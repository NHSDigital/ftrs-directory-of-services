# Resource names
sandbox_lambda_name = "sandbox-lambda"

# Lambda
sandbox_lambda_runtime     = "python3.12"
sandbox_lambda_timeout     = 30
sandbox_lambda_memory_size = 512
sandbox_lambda_handler     = "handler.handler"

#S3
sandbox_store_bucket_name = "sandbox-store"
s3_versioning             = false

# API Gateway
api_gateway_authorization_type         = "AWS_IAM"
api_gateway_payload_format_version     = "2.0"
api_gateway_integration_timeout        = 10000
api_gateway_access_logs_retention_days = 7
api_gateway_throttling_burst_limit     = 100
api_gateway_throttling_rate_limit      = 10
