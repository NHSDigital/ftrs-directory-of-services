# resource "aws_cloudwatch_log_subscription_filter" "to_splunk" {
#   for_each = var.log_groups
#   name            = "${var.project}-${var.environment}-subscription${replace(each.value, "/", "-")}"
#   log_group_name  = each.value
#   filter_pattern  = "" # empty = all logs
#   destination_arn = aws_kinesis_firehose_delivery_stream.splunk.arn
#   role_arn        = aws_iam_role.cw_to_firehose_role.arn
# }
# name from module
# data look ups
# boolean to pass
# build where we build log groups with logic to decide if subs needed
