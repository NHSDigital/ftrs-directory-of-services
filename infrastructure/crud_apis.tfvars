# Resource names
s3_bucket_name                     = "crud-apis-s3"
organisation_api_lambda_name       = "organisations-lambda"
healthcare_service_api_lambda_name = "healthcare-service-lambda"
location_api_lambda_name           = "locations-lambda"

#Lambda
organisation_api_lambda_runtime           = "python3.12"
organisation_api_lambda_timeout           = 30
organisation_api_lambda_memory_size       = 512
organisation_api_lambda_handler           = "organisations/lambda_handler.handler"
healthcare_service_api_lambda_runtime     = "python3.12"
healthcare_service_api_lambda_timeout     = 30
healthcare_service_api_lambda_memory_size = 512
healthcare_service_api_lambda_handler     = "healthcare_service/app/handler_healthcare_service.handler"
location_api_lambda_runtime               = "python3.12"
location_api_lambda_timeout               = 30
location_api_lambda_memory_size           = 512
location_api_lambda_handler               = "locations/app/handler_locations.handler"

#S3
crud_apis_store_bucket_name = "crud-api-store"
s3_versioning               = false
