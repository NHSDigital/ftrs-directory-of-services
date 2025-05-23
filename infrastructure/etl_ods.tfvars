team_owner                          = "data-sourcing"
lambda_runtime                      = "python3.12"
extract_name                        = "processor-lambda"
processor_lambda_handler            = "pipeline.processor.lambda_handler"
processor_lambda_connection_timeout = 900
processor_lambda_memory_size        = 512
etl_ods_pipeline_store_bucket_name  = "pipeline-store"
s3_versioning                       = false

aws_lambda_layers = [
  "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:16"
]

delay_seconds              = 10
visibility_timeout_seconds = 30
max_message_size           = 2048
message_retention_seconds  = 86400
receive_wait_time_seconds  = 2
sqs_managed_sse_enabled    = true
