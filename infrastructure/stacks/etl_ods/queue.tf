resource "aws_sqs_queue" "dead_letter_queue" {
  name                       = "${local.resource_prefix}-dead-letter-queue${local.workspace_suffix}"
  delay_seconds              = var.delay_seconds
  visibility_timeout_seconds = var.visibility_timeout_seconds
  max_message_size           = var.max_message_size
  message_retention_seconds  = var.message_retention_seconds
  receive_wait_time_seconds  = var.receive_wait_time_seconds
  sqs_managed_sse_enabled    = var.sqs_managed_sse_enabled

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "sqs.amazonaws.com" }
        Action    = "sqs:SendMessage"
        Resource  = "*"
      }
    ]
  })
}

resource "aws_sqs_queue" "transformed_queue" {
  name                       = "${local.resource_prefix}-queue${local.workspace_suffix}"
  delay_seconds              = var.delay_seconds
  visibility_timeout_seconds = var.visibility_timeout_seconds
  max_message_size           = var.max_message_size
  message_retention_seconds  = var.message_retention_seconds
  receive_wait_time_seconds  = var.receive_wait_time_seconds
  sqs_managed_sse_enabled    = var.sqs_managed_sse_enabled
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dead_letter_queue.arn
    maxReceiveCount     = var.max_receive_count
  })
}
