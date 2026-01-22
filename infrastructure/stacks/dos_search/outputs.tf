output "dos_search_waf_web_acl_arn" {
  description = "ARN of the dos-search regional WAFv2 Web ACL"
  value       = aws_wafv2_web_acl.dos_search_web_acl.arn
}

output "dos_search_waf_log_group_name" {
  description = "CloudWatch Log Group name receiving WAF logs"
  value       = aws_cloudwatch_log_group.waf_log_group.name
}

output "dos_search_waf_pingdom_ip_set_arn" {
  description = "ARN of the Pingdom IP set (null if disabled)"
  value       = local.enable_pingdom_allowlist ? aws_wafv2_ip_set.pingdom_ips[0].arn : null
}

output "dos_search_waf_statuscake_ip_set_arn" {
  description = "ARN of the StatusCake IP set (null if disabled)"
  value       = local.enable_statuscake_allowlist ? aws_wafv2_ip_set.statuscake_ips[0].arn : null
}
