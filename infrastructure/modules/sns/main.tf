resource "aws_sns_topic" "topic" {
  name              = var.topic_name
  display_name      = var.display_name
  kms_master_key_id = var.kms_key_id

  tags = var.tags
}

resource "aws_sns_topic_policy" "topic_policy" {
  arn = aws_sns_topic.topic.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.topic.arn
      }
    ]
  })
}
