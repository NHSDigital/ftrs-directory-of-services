gp_search_service_name = "ftrs-dos-gp-search"

# Resource names
s3_bucket_name           = "gp-search-s3"
lambda_name              = "gp-search-lambda"
health_check_lambda_name = "health-check-lambda"

#Lambda
lambda_runtime     = "python3.12"
lambda_timeout     = 900
lambda_memory_size = 512

#DynamoDB
dynamodb_organisation_table_name = "ftrs-dos-dev-database-organisation-is"

eu_west_2_api_gateway_zone_id = "ZJ5UAJN8Y3Z2Q"
