resource "aws_kinesis_firehose_delivery_stream" "splunk" {
  name        = "${local.resource_prefix}-${var.firehose_name}"
  destination = "splunk"

  depends_on = [aws_lambda_permission.firehose_invoke_splunk_hec_transformer]

  server_side_encryption {
    enabled  = var.enable_firehose_sse
    key_type = var.enable_firehose_sse ? "CUSTOMER_MANAGED_CMK" : null
    key_arn  = var.enable_firehose_sse ? module.firehose_encryption_key.arn : null
  }

  splunk_configuration {
    hec_endpoint               = "${var.splunk_collector_url}${var.splunk_hec_endpoint}"
    hec_token                  = var.splunk_hec_token
    hec_acknowledgment_timeout = var.hec_acknowledgment_timeout
    hec_endpoint_type          = "Event"
    retry_duration             = var.retry_duration
    s3_backup_mode             = var.s3_backup_mode


    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose_log_group.name
      log_stream_name = "SplunkDelivery"
    }

    s3_configuration {
      role_arn           = aws_iam_role.firehose_role.arn
      bucket_arn         = module.firehose_backup_s3.s3_bucket_arn
      prefix             = "event/"
      buffering_interval = 300
      buffering_size     = 5
      compression_format = "GZIP"
    }

    processing_configuration {
      enabled = true

      processors {
        type = "Decompression"

        parameters {
          parameter_name  = "CompressionFormat"
          parameter_value = "GZIP"
        }
      }

      processors {
        type = "Lambda"

        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = aws_lambda_function.splunk_hec_transformer.arn
        }
      }
    }
  }
}
