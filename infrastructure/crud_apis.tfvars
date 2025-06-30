# Resource names
s3_bucket_name                     = "crud-apis-s3"
organisation_api_lambda_name       = "organisations-lambda"
healthcare_service_api_lambda_name = "healthcare-service-lambda"
location_api_lambda_name           = "location-lambda"

# Lambda
organisation_api_lambda_runtime           = "python3.12"
organisation_api_lambda_timeout           = 30
organisation_api_lambda_memory_size       = 512
organisation_api_lambda_handler           = "organisations/app/handler_organisation.handler"
healthcare_service_api_lambda_runtime     = "python3.12"
healthcare_service_api_lambda_timeout     = 30
healthcare_service_api_lambda_memory_size = 512
healthcare_service_api_lambda_handler     = "healthcare_service/app/handler_healthcare_service.handler"
location_api_lambda_runtime               = "python3.12"
location_api_lambda_timeout               = 30
location_api_lambda_memory_size           = 512
location_api_lambda_handler               = "location/app/handler_location.handler"

#S3
crud_apis_store_bucket_name = "crud-api-store"
s3_versioning               = false

# API Gateway
api_gateway_authorization_type        = "AWS_IAM"
api_gateway_payload_format_version    = "2.0"
api_gateway_integration_timeout       = 10000
api_gateway_access_log_retention_days = 7
api_gateway_throttling_burst_limit    = 100
api_gateway_throttling_rate_limit     = 10

hosted_zone_id = "Z1041066BVJJ75SAJKKV"
