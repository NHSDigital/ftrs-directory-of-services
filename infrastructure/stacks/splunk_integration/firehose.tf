resource "aws_kinesis_firehose_delivery_stream" "splunk" {
  name        = var.firehose_name
  destination = "splunk"
  # server_side_encryption {
  #   enabled = true
  #   key_type = CUSTOMER_MANAGED_CMK
  #   key_arn  = var.firehose_kms_key_arn

  # }
  # TODO
  splunk_configuration {
    hec_endpoint               = "${aws_ssm_parameter.splunk_hec_endpoint_url[0].value}${aws_ssm_parameter.splunk_hec_endpoint_app[0].value}"
    hec_token                  = var.splunk_hec_token_app
    hec_acknowledgment_timeout = 300
    hec_endpoint_type          = "Raw" # "Event" also supported

    retry_duration = 300

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose_error_log_group.name
      log_stream_name = "SplunkDelivery"
    }
    # alternative to s3 ?
    s3_backup_mode = "FailedEventsOnly"

    s3_configuration {
      role_arn           = aws_iam_role.firehose_role[0].arn
      bucket_arn         = module.firehose_backup_s3[0].s3_bucket_arn
      buffering_interval = 300
      buffering_size     = 5
      compression_format = "GZIP"
    }
  }
}
