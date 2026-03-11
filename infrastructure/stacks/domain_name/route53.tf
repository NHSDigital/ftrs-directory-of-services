resource "aws_route53_zone" "root_zone" {
  # checkov:skip=CKV2_AWS_38: TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-383
  # checkov:skip=CKV2_AWS_39: TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-383
  count = var.environment == "mgmt" ? 1 : 0
  name  = var.root_domain_name
}

resource "aws_route53_zone" "environment_zone" {
  # checkov:skip=CKV2_AWS_38: TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-383
  # checkov:skip=CKV2_AWS_39: TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-383
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

resource "aws_route53_health_check" "environment_zone" {
  # checkov:skip=CKV2_AWS_49: alarm notification is handled via CloudWatch alarms and SNS
  count             = var.environment == "mgmt" ? 0 : 1
  fqdn              = local.root_domain_name
  port              = 443
  type              = "HTTPS"
  resource_path     = "/"
  failure_threshold = var.route53_health_check_failure_threshold
  request_interval  = var.route53_health_check_request_interval
  measure_latency   = true

  tags = {
    Name = "${local.resource_prefix}-environment-zone-health-check"
  }
}

resource "aws_route53_health_check" "root_zone" {
  # checkov:skip=CKV2_AWS_49: alarm notification is handled via CloudWatch alarms and SNS
  count             = var.environment == "mgmt" ? 0 : 1
  fqdn              = var.root_domain_name
  port              = 443
  type              = "HTTPS"
  resource_path     = "/"
  failure_threshold = var.route53_health_check_failure_threshold
  request_interval  = var.route53_health_check_request_interval
  measure_latency   = true

  tags = {
    Name = "${local.resource_prefix}-root-zone-health-check"
  }
}
