team_owner = "fd"

migration_pipeline_store_bucket_name = "pipeline-store"
s3_versioning                        = false

source_rds_database = "data_migration"
target_rds_database = "Core"
rds_port            = 5432
rds_engine          = "aurora-postgresql"
rds_engine_version  = "16.4"
rds_engine_mode     = "provisioned"
rds_instance_class  = "db.serverless"

lambda_runtime                      = "python3.12"
data_collection_date                = "05-03-25"
extract_name                        = "extract-lambda"
extract_lambda_handler              = "extract.lambda_handler"
extract_lambda_connection_timeout   = 900
extract_lambda_memory_size          = 512
transform_name                      = "transform-lambda"
transform_lambda_handler            = "transform.lambda_handler"
transform_lambda_connection_timeout = 900
transform_lambda_memory_size        = 512
load_name                           = "load-lambda"
load_lambda_handler                 = "load.lambda_handler"
load_lambda_connection_timeout      = 900
load_lambda_memory_size             = 512

aws_lambda_layers = [
  "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:16"
]
