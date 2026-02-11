module "sns_topic" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-sns.git?ref=84b777952d08caa7ce06a4ef53aafdcc03cfc165"

  name              = var.topic_name
  display_name      = var.display_name
  kms_master_key_id = var.kms_key_id

  topic_policy_statements = {
    cloudwatch = {
      actions = ["SNS:Publish"]
      principals = [{
        type        = "Service"
        identifiers = ["cloudwatch.amazonaws.com"]
      }]
    }
  }

  subscriptions = var.subscriptions

  tags = var.tags
}
