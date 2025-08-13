resource "aws_sqs_queue" "dms_event_queue" {
  # checkov:skip=CKV_AWS_27: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-545
  name                    = "${local.resource_prefix}-${var.dms_event_queue_name}${local.workspace_suffix}"
  sqs_managed_sse_enabled = true
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dms_event_queue_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "dms_event_queue_dlq" {
  name                    = "${local.resource_prefix}-${var.dms_event_queue_name}-dlq${local.workspace_suffix}"
  sqs_managed_sse_enabled = true
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

resource "aws_sqs_queue" "eventbridge_event_full_migration_completion_dlq" {
  count = local.is_primary_environment ? 1 : 0

  name                    = "${local.resource_prefix}-${var.full_migration_completion_event_queue_name}-dlq"
  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue_policy" "eventbridge_event_full_migration_completion_dlq_policy" {
  queue_url = aws_sqs_queue.eventbridge_event_full_migration_completion_dlq.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "events.amazonaws.com"
        },
        Action   = ["sqs:SendMessage"],
        Resource = aws_sqs_queue.eventbridge_event_full_migration_completion_dlq.arn,
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_cloudwatch_event_rule.dms_full_replication_task_completed[0].arn
          }
        }
      }
    ]
  })
}
