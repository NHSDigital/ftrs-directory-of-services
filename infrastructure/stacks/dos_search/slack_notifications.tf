# Subscribe dos_search alarms to centralized slack_notifier SNS topic
# Requires slack_notifier stack to be deployed first

data "terraform_remote_state" "slack_notifier" {
  count   = var.enable_slack_notifications ? 1 : 0
  backend = "s3"

  config = {
    bucket         = "nhse-${var.environment}-${var.repo_name}-terraform-state"
    key            = "slack_notifier/terraform.state"
    region         = var.aws_region
    dynamodb_table = "nhse-${var.environment}-${var.repo_name}-terraform-state-lock"
    encrypt        = true
  }
}

resource "aws_sns_topic_subscription" "lambda_alarms_to_slack" {
  count     = var.enable_slack_notifications ? 1 : 0
  topic_arn = module.lambda_monitoring.sns_topic_arn
  protocol  = "sns"
  endpoint  = data.terraform_remote_state.slack_notifier[0].outputs.sns_topic_arn
}
