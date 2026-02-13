module "sns_topic" {
  #Module version: 6.2.1
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-sns.git?ref=544e3127146aa77a349b8b84a792b196f19d609a"

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
