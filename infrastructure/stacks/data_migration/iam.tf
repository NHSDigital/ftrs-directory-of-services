data "aws_iam_policy_document" "rds_event_listener_sqs_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = [
      aws_sqs_queue.rds_event_listener.arn
    ]
  }
}

resource "aws_iam_role" "rds_lambda_invoke_role" {
  count = local.deploy_databases ? 1 : 0
  name  = "${local.resource_prefix}-${var.rds_event_listener_name}-invoke-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "rds.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "rds_lambda_invoke_policy" {
  count = local.deploy_databases ? 1 : 0
  name  = "${local.resource_prefix}-${var.rds_event_listener_name}-invoke-policy"
  role  = aws_iam_role.rds_lambda_invoke_role[0].id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = "lambda:InvokeFunction",
      Resource = module.rds_event_listener_lambda[0].lambda_function_arn
    }]
  })
}
