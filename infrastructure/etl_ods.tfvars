team_owner                          = "data-sourcing"
lambda_runtime                      = "python3.12"
extract_name                        = "processor-lambda"
processor_lambda_handler            = "pipeline.processor.lambda_handler"
processor_lambda_connection_timeout = 900
processor_lambda_memory_size        = 512
etl_ods_pipeline_store_bucket_name  = "pipeline-store"
s3_versioning                       = false

