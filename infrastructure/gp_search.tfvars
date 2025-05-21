gp_search_service_name = "ftrs-dos-gp-search"

# Resource names
s3_bucket_name = "gp-search-s3"
lambda_name    = "gp-search-lambda"

#Lambda
lambda_runtime     = "python3.12"
lambda_timeout     = 900
lambda_memory_size = 512

#DynamoDB
dynamodb_organisation_table_name = "ftrs-dos-dev-database-organisation-is"

# Dependency layers
aws_lambda_layers = [
  "arn:aws:serverlessrepo:eu-west-1:057560766410:applications/aws-lambda-powertools-python-layer-v3-python312-x86-64"
]
