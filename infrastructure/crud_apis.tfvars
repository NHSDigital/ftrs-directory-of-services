# Resource names
s3_bucket_name                     = "crud-apis-s3"
organisation_api_lambda_name       = "organisations-lambda"
healthcare_service_api_lambda_name = "healthcare-service-lambda"

#Lambda
organisation_api_lambda_runtime           = "python3.12"
organisation_api_lambda_timeout           = 30
organisation_api_lambda_memory_size       = 512
organisation_api_lambda_handler           = "organisations/lambda_handler.handler"
healthcare_service_api_lambda_runtime     = "python3.12"
healthcare_service_api_lambda_timeout     = 30
healthcare_service_api_lambda_memory_size = 512
healthcare_service_api_lambda_handler     = "locations/app/handler_healthcare.handler"

#S3
crud_apis_store_bucket_name = "crud-api-store"
s3_versioning               = false
