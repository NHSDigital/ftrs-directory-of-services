main_project = "ftrs-directory-of-services"
project      = "ftrs-dos-data-migration"

migration_pipeline_store_bucket_name = "pipeline-store"
s3_versioning                        = false

source_rds_database = "data_migration"
target_rds_database = "Core"
rds_port            = 5432
rds_engine          = "aurora-postgresql"
rds_engine_version  = "16.4"
rds_engine_mode     = "provisioned"
rds_instance_class  = "db.serverless"

lambda_runtime = "python3.12"
