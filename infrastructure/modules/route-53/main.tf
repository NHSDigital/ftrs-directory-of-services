resource "aws_route53_zone" "cm" {
  # checkov:skip=CKV2_AWS_38: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-409
  # checkov:skip=CKV2_AWS_39: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-409
  name    = var.zone_name
  comment = var.comment
}
