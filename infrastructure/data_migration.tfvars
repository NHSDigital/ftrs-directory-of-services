team_owner = "future-directory"

migration_pipeline_store_bucket_name = "pipeline-store"
s3_versioning                        = false
dynamodb_exports_s3_expiration_days  = 30

source_rds_database  = "pathwaysdos_future"
target_rds_database  = "dos"
replica_rds_database = "data_migration"
rds_engine           = "aurora-postgresql"
rds_engine_version   = "16.8"
rds_engine_mode      = "provisioned"
rds_instance_class   = "db.serverless"

lambda_runtime               = "python3.12"
data_collection_date         = "05-03-25"
processor_lambda_name        = "processor-lambda"
processor_lambda_handler     = "service_migration.lambda_handler.lambda_handler"
processor_lambda_timeout     = 30
processor_lambda_memory_size = 1024

queue_populator_lambda_name        = "queue-populator-lambda"
queue_populator_lambda_timeout     = 300
queue_populator_lambda_memory_size = 2048
queue_populator_lambda_handler     = "queue_populator.lambda_handler.lambda_handler"

dms_event_queue_name                               = "dms-events"
dms_event_queue_enabled                            = true
dms_event_queue_batch_size                         = 50
dms_event_queue_maximum_batching_window_in_seconds = 1
dms_event_queue_maximum_concurrency                = 20

aws_lambda_layers = [
  "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:16"
]

data_migration_rds_min_capacity = 1
data_migration_rds_max_capacity = 7

rds_event_listener_lambda_name               = "rds-event-listener"
rds_event_listener_lambda_connection_timeout = 300
rds_event_listener_lambda_memory_size        = 1024

schema_name                      = "pathwaysdos"
sqs_ssm_path_for_ids             = "/ftrs-dos/migration/sqs-ids/"
migration_copy_db_lambda_trigger = "record_change_trigger.lambda_handler.lambda_handler"

dms_db_lambda_name               = "dms-db-setup"
dms_db_lambda_trigger            = "dms_provisioner.lambda_handler.lambda_handler"
dms_db_lambda_connection_timeout = 300
dms_db_lambda_memory_size        = 1024

full_migration_completion_event_queue_name = "full-migration-completion-event"
target_rds_credentials                     = "target-rds-credentials"
dms_user_password                          = "dms-user-password"
source_rds_credentials                     = "source-rds-credentials"
replica_rds_credentials                    = "replica-rds-credentials"

dms_replication_instance_class = "dms.t3.small"
dms_engine                     = "aurora-postgresql"
dms_allocated_storage          = 100
full_migration_type            = "full-load"
cdc_migration_type             = "cdc"
