resource "aws_route53_zone" "cm" {
  # checkov:skip=CKV2_AWS_38: Temp suppression JIRA-445
  # checkov:skip=CKV2_AWS_39: Temp suppression JIRA-445
  name    = var.zone_name
  comment = var.comment
}
