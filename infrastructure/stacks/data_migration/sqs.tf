resource "aws_sqs_queue" "dms_event_queue" {
  # checkov:skip=CKV_AWS_27: Temp suppression JIRA-445
  name = "${local.resource_prefix}-${var.dms_event_queue_name}${local.workspace_suffix}"
}

resource "aws_sqs_queue_policy" "dms_event_queue_policy" {
  queue_url = aws_sqs_queue.dms_event_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action   = ["sqs:SendMessage", "sqs:ReceiveMessage"],
        Resource = aws_sqs_queue.dms_event_queue.arn,
      }
    ]
  })
}
