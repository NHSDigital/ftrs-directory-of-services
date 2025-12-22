# ============================================================================
# CloudWatch Log Insights Query Definitions for ODS ETL Pipeline
# ============================================================================

# -----------------------------------------------------------------------------
# Query: Track all ODS ETL Pipeline logs by Request ID
# Use case: Collate all ETL pipeline logs (including Ingest API) for a given request ID
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_query_definition" "etl_pipeline_by_request_id" {
  name = "FTRS/ETL-ODS/${var.environment}/Track-Pipeline-By-Request-ID"

  log_group_names = [
    module.processor_lambda.lambda_cloudwatch_log_group_name,
    module.consumer_lambda.lambda_cloudwatch_log_group_name,
    "/aws/lambda/${local.project_prefix}-crud-apis-organisations-lambda${local.workspace_suffix}",
  ]

  query_string = <<-QUERY
    fields @timestamp, @message, @logStream, @log
    | filter request_id like /$$REQUEST_ID$$/
    | parse @message '"log_reference":"*"' as log_reference
    | parse @message '"message":"*"' as log_message
    | parse @message '"etl_stage":"*"' as etl_stage
    | parse @message '"lambda_name":"*"' as lambda_name
    | parse @message '"duration_ms":*,' as duration_ms
    | parse @message '"correlation_id":"*"' as correlation_id
    | parse @message '"error_message":"*"' as error_message
    | sort @timestamp asc
    | display @timestamp, log_reference, log_message, etl_stage, lambda_name, duration_ms, correlation_id, request_id, error_message, @log
  QUERY
}

# -----------------------------------------------------------------------------
# Query: Track all ODS ETL Pipeline logs by Correlation ID
# Use case: Track a complete ETL run across all services
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_query_definition" "etl_pipeline_by_correlation_id" {
  name = "FTRS/ETL-ODS/${var.environment}/Track-Pipeline-By-Correlation-ID"

  log_group_names = [
    module.processor_lambda.lambda_cloudwatch_log_group_name,
    module.consumer_lambda.lambda_cloudwatch_log_group_name,
    "/aws/lambda/${local.project_prefix}-crud-apis-organisations-lambda${local.workspace_suffix}",
  ]

  query_string = <<-QUERY
    fields @timestamp, @message, @logStream, @log
    | filter correlation_id like /$$CORRELATION_ID$$/
    | parse @message '"log_reference":"*"' as log_reference
    | parse @message '"message":"*"' as log_message
    | parse @message '"etl_stage":"*"' as etl_stage
    | parse @message '"lambda_name":"*"' as lambda_name
    | parse @message '"duration_ms":*,' as duration_ms
    | parse @message '"request_id":"*"' as request_id
    | parse @message '"error_message":"*"' as error_message
    | sort @timestamp asc
    | display @timestamp, log_reference, log_message, etl_stage, lambda_name, duration_ms, correlation_id, request_id, error_message, @log
  QUERY
}

# -----------------------------------------------------------------------------
# Query: Track Ingest API logs by Request ID
# Use case: Collate all Ingest API logs for a given request ID
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_query_definition" "ingest_api_by_request_id" {
  name = "FTRS/Ingest-API/${var.environment}/Track-By-Request-ID"

  log_group_names = [
    "/aws/lambda/${local.project_prefix}-crud-apis-organisations-lambda${local.workspace_suffix}",
  ]

  query_string = <<-QUERY
    fields @timestamp, @message, @logStream
    | filter request_id like /$$REQUEST_ID$$/
    | parse @message '"log_reference":"*"' as log_reference
    | parse @message '"message":"*"' as log_message
    | parse @message '"status_code":*,' as status_code
    | parse @message '"duration_ms":*,' as duration_ms
    | parse @message '"correlation_id":"*"' as correlation_id
    | parse @message '"error_message":"*"' as error_message
    | sort @timestamp asc
    | display @timestamp, log_reference, log_message, status_code, duration_ms, correlation_id, request_id, error_message
  QUERY
}

# -----------------------------------------------------------------------------
# Query: ETL Pipeline Start/End Timeline
# Use case: Monitor ETL run duration and status with clear start/end markers
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_query_definition" "etl_pipeline_timeline" {
  name = "FTRS/ETL-ODS/${var.environment}/Pipeline-Start-End-Timeline"

  log_group_names = [
    module.processor_lambda.lambda_cloudwatch_log_group_name,
    module.consumer_lambda.lambda_cloudwatch_log_group_name,
  ]

  query_string = <<-QUERY
    fields @timestamp, @message, @logStream
    | filter @message like /ETL_PIPELINE_START/ or @message like /ETL_PIPELINE_END/ or @message like /ETL_PROCESSOR_START/ or @message like /ETL_CONSUMER_BATCH_COMPLETE/
    | parse @message '"log_reference":"*"' as log_reference
    | parse @message '"message":"*"' as log_message
    | parse @message '"etl_stage":"*"' as etl_stage
    | parse @message '"lambda_name":"*"' as lambda_name
    | parse @message '"duration_ms":*,' as duration_ms
    | parse @message '"correlation_id":"*"' as correlation_id
    | parse @message '"request_id":"*"' as request_id
    | parse @message '"etl_run_status":"*"' as etl_run_status
    | sort @timestamp desc
    | display @timestamp, log_reference, log_message, etl_stage, lambda_name, duration_ms, correlation_id, request_id, etl_run_status
    | limit 100
  QUERY
}

# -----------------------------------------------------------------------------
# Query: ETL Pipeline Errors
# Use case: Monitor and debug ETL failures
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_query_definition" "etl_pipeline_errors" {
  name = "FTRS/ETL-ODS/${var.environment}/Pipeline-Errors"

  log_group_names = [
    module.processor_lambda.lambda_cloudwatch_log_group_name,
    module.consumer_lambda.lambda_cloudwatch_log_group_name,
    "/aws/lambda/${local.project_prefix}-crud-apis-organisations-lambda${local.workspace_suffix}",
  ]

  query_string = <<-QUERY
    fields @timestamp, @message, @logStream, @log
    | filter @message like /ERROR/ or @message like /"level":"ERROR"/ or @message like /Exception/
    | parse @message '"log_reference":"*"' as log_reference
    | parse @message '"message":"*"' as log_message
    | parse @message '"error_message":"*"' as error_message
    | parse @message '"correlation_id":"*"' as correlation_id
    | parse @message '"request_id":"*"' as request_id
    | parse @message '"lambda_name":"*"' as lambda_name
    | sort @timestamp desc
    | display @timestamp, log_reference, log_message, error_message, lambda_name, correlation_id, request_id, @log
    | limit 100
  QUERY
}

# -----------------------------------------------------------------------------
# Query: ETL Pipeline Performance Metrics
# Use case: Monitor ETL performance over time
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_query_definition" "etl_pipeline_performance" {
  name = "FTRS/ETL-ODS/${var.environment}/Pipeline-Performance"

  log_group_names = [
    module.processor_lambda.lambda_cloudwatch_log_group_name,
    module.consumer_lambda.lambda_cloudwatch_log_group_name,
  ]

  query_string = <<-QUERY
    fields @timestamp, @message
    | filter @message like /ETL_PIPELINE_END/ or @message like /ETL_CONSUMER_BATCH_COMPLETE/
    | parse @message '"duration_ms":*,' as duration_ms
    | parse @message '"total_records":*,' as total_records
    | parse @message '"successful_count":*,' as successful_count
    | parse @message '"failed_count":*,' as failed_count
    | parse @message '"etl_run_status":"*"' as status
    | stats avg(duration_ms) as avg_duration_ms,
            max(duration_ms) as max_duration_ms,
            min(duration_ms) as min_duration_ms,
            sum(total_records) as total_records_processed,
            sum(successful_count) as total_successful,
            sum(failed_count) as total_failed,
            count(*) as run_count
      by bin(1h)
    | sort @timestamp desc
  QUERY
}
