team_owner = "future-directory"

migration_pipeline_store_bucket_name = "pipeline-store"
s3_versioning                        = false

source_rds_database = "data_migration"
target_rds_database = "Core"
rds_port            = 5432
rds_engine          = "aurora-postgresql"
rds_engine_version  = "16.6"
rds_engine_mode     = "provisioned"
rds_instance_class  = "db.serverless"

lambda_runtime                     = "python3.12"
data_collection_date               = "05-03-25"
migration_lambda_name              = "lambda"
migration_lambda_handler           = "pipeline.lambda_handler.lambda_handler"
migration_lambda_timeout           = 30
migration_lambda_memory_size       = 1024
queue_populator_lambda_name        = "queue-populator-lambda"
queue_populator_lambda_timeout     = 300
queue_populator_lambda_memory_size = 2048
queue_populator_lambda_handler     = "pipeline.queue_populator.lambda_handler"

migration_queue_enabled                            = true
migration_queue_batch_size                         = 50
migration_queue_maximum_batching_window_in_seconds = 1
migration_queue_maximum_concurrency                = 20

aws_lambda_layers = [
  "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:16"
]

data_migration_rds_min_capacity = 1
data_migration_rds_max_capacity = 5
