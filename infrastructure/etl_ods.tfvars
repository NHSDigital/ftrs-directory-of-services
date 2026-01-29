team_owner     = "data-sourcing"
lambda_runtime = "python3.12"

# Extract Lambda
extractor_name                      = "extractor-lambda"
extractor_lambda_handler            = "extractor.extractor.extractor_lambda_handler"
extractor_lambda_connection_timeout = 150

# Transform Lambda
transformer_name                      = "transformer-lambda"
transformer_lambda_handler            = "transformer.transformer.transformer_lambda_handler"
transformer_lambda_connection_timeout = 150

# Consumer Lambda
consumer_name                      = "consumer-lambda"
consumer_lambda_handler            = "consumer.consumer.consumer_lambda_handler"
consumer_lambda_connection_timeout = 150

lambda_memory_size                 = 512
etl_ods_pipeline_store_bucket_name = "pipeline-store"
s3_versioning                      = false


delay_seconds              = 10
visibility_timeout_seconds = 900
max_message_size           = 10240
message_retention_seconds  = 86400
receive_wait_time_seconds  = 2

max_receive_count  = 5
ods_api_page_limit = 1000
