main_project           = "ftrs-directory-of-services"
project                = "ftrs-dos-integrated-search"
gp_search_service_name = "ftrs-dos-gp-search"

# Resource names
s3_bucket_name = "gp-search-s3"
lambda_name    = "gp-search-lambda"

#Lambda
lambda_runtime = "python3.12"
db_secret_name = "/ftrs-dos-data-migration/dev/target-rds-credentials"

#RDS
rds_port = 5432

# Dependency layers
aws_lambda_layers = [
  "arn:aws:lambda:eu-west-2:017000801446:layer:AWSLambdaPowertoolsPythonV2:46"
]
