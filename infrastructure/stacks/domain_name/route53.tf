resource "aws_route53_zone" "root_zone" {
  # checkov:skip=CKV2_AWS_38: Temp suppression JIRA-445
  # checkov:skip=CKV2_AWS_39: Temp suppression JIRA-445
  count = var.environment == "mgmt" ? 1 : 0
  name  = var.root_domain_name
}

resource "aws_route53_zone" "environment_zone" {
  # checkov:skip=CKV2_AWS_38: Temp suppression JIRA-445
  # checkov:skip=CKV2_AWS_39: Temp suppression JIRA-445
  count = var.environment == "mgmt" ? 0 : 1
  name  = local.root_domain_name
}

data "aws_route53_zone" "root_zone" {
  provider = aws.mgmt
  count    = var.environment == "mgmt" ? 0 : 1
  name     = var.root_domain_name
}

resource "aws_route53_record" "environment_zone_delegation" {
  provider = aws.mgmt
  count    = var.environment == "mgmt" ? 0 : 1
  zone_id  = data.aws_route53_zone.root_zone[0].zone_id
  name     = aws_route53_zone.environment_zone[0].name
  type     = "NS"
  ttl      = 300
  records  = aws_route53_zone.environment_zone[0].name_servers
}
