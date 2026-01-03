resource "aws_sqs_queue" "load_dead_letter_queue" {
  name                       = "${local.resource_prefix}-load-dlq${local.workspace_suffix}"
  delay_seconds              = var.delay_seconds
  visibility_timeout_seconds = var.visibility_timeout_seconds
  max_message_size           = var.max_message_size
  message_retention_seconds  = var.message_retention_seconds
  receive_wait_time_seconds  = var.receive_wait_time_seconds
  kms_master_key_id          = data.aws_kms_key.sqs_kms_alias.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "sqs.amazonaws.com" }
        Action    = "sqs:SendMessage"
        Resource  = "arn:aws:sqs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${local.resource_prefix}-dlq${local.workspace_suffix}"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = "${data.aws_caller_identity.current.account_id}"
          }
        }
      }
    ]
  })
}

resource "aws_sqs_queue" "load_queue" {
  name                       = "${local.resource_prefix}-load-queue${local.workspace_suffix}"
  delay_seconds              = var.delay_seconds
  visibility_timeout_seconds = var.visibility_timeout_seconds
  max_message_size           = var.max_message_size
  message_retention_seconds  = var.message_retention_seconds
  receive_wait_time_seconds  = var.receive_wait_time_seconds
  kms_master_key_id          = data.aws_kms_key.sqs_kms_alias.arn
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.load_dead_letter_queue.arn
    maxReceiveCount     = var.max_receive_count
  })
}

resource "aws_sqs_queue" "transform_dead_letter_queue" {
  name                       = "${local.resource_prefix}-transform-dlq${local.workspace_suffix}"
  delay_seconds              = var.delay_seconds
  visibility_timeout_seconds = var.visibility_timeout_seconds
  max_message_size           = var.max_message_size
  message_retention_seconds  = var.message_retention_seconds
  receive_wait_time_seconds  = var.receive_wait_time_seconds
  kms_master_key_id          = data.aws_kms_key.sqs_kms_alias.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "sqs.amazonaws.com" }
        Action    = "sqs:SendMessage"
        Resource  = "arn:aws:sqs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${local.resource_prefix}-dlq${local.workspace_suffix}"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = "${data.aws_caller_identity.current.account_id}"
          }
        }
      }
    ]
  })
}

resource "aws_sqs_queue" "transform_queue" {
  name                       = "${local.resource_prefix}-transform-queue${local.workspace_suffix}"
  delay_seconds              = var.delay_seconds
  visibility_timeout_seconds = var.visibility_timeout_seconds
  max_message_size           = var.max_message_size
  message_retention_seconds  = var.message_retention_seconds
  receive_wait_time_seconds  = var.receive_wait_time_seconds
  kms_master_key_id          = data.aws_kms_key.sqs_kms_alias.arn
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.transform_dead_letter_queue.arn
    maxReceiveCount     = var.max_receive_count
  })
}
