resource "aws_sns_topic" "alarms" {
  name              = var.sns_topic_name
  display_name      = var.sns_display_name
  kms_master_key_id = var.kms_key_id

  tags = var.tags
}

resource "aws_sns_topic_policy" "alarms" {
  arn = aws_sns_topic.alarms.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowCloudWatchPublish"
      Effect = "Allow"
      Principal = {
        Service = "cloudwatch.amazonaws.com"
      }
      Action   = "SNS:Publish"
      Resource = aws_sns_topic.alarms.arn
    }]
  })
}
