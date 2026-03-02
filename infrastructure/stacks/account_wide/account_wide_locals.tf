# Define interface endpoint services for loop
locals {
  interface_vpc_endpoints = {
    sqs            = "sqs"
    ssm            = "ssm"
    ssmmessages    = "ssmmessages"
    ec2messages    = "ec2messages"
    kms            = "kms"
    secretsmanager = "secretsmanager"
    rds            = "rds"
    appconfig      = "appconfig"
    appconfigdata  = "appconfigdata"
    lambda         = "lambda"
    logs           = "logs"
  }

  apim_apigee_allowlist_cidrs   = distinct(compact(var.apim_apigee_cidrs))
  ec2_allowlist_cidrs           = distinct(compact(concat(var.ec2_whitelist_cidrs, [for ip in module.vpc.nat_public_ips : "${ip}/32"])))
  apim_apigee_allowlist_enabled = length(local.apim_apigee_allowlist_cidrs) > 0
  ec2_allowlist_enabled         = length(local.ec2_allowlist_cidrs) > 0
  regional_allowlist_cidrs      = distinct(compact(concat(local.apim_apigee_allowlist_cidrs, local.ec2_allowlist_cidrs)))
  regional_allowlist_enabled    = length(local.regional_allowlist_cidrs) > 0
  allowlist_ipset_arns = compact([
    local.apim_apigee_allowlist_enabled ? aws_wafv2_ip_set.apim_apigee_whitelist_regional[0].arn : null,
    local.ec2_allowlist_enabled ? aws_wafv2_ip_set.ec2_whitelist_regional[0].arn : null,
  ])
  allowlist_ipset_count = length(local.allowlist_ipset_arns)
}
