resource "aws_sqs_queue" "rds_event_listener_dlq" {
  name                    = "${local.resource_prefix}-rds-events-dlq${local.workspace_suffix}"
  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue" "rds_event_listener" {
  name                    = "${local.resource_prefix}-rds-events${local.workspace_suffix}"
  sqs_managed_sse_enabled = true
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.rds_event_listener_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue_policy" "rds_event_listener_policy" {
  queue_url = aws_sqs_queue.rds_event_listener.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action   = "sqs:SendMessage",
        Resource = aws_sqs_queue.rds_event_listener.arn
      }
    ]
  })
}
