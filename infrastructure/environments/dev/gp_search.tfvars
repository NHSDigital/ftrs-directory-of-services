lambda_cloudwatch_logs_retention_days              = 30
health_check_lambda_cloudwatch_logs_retention_days = 30
api_gateway_access_logs_retention_days             = 30

jmeter_poweroff_after_setup = true

# Enable SSM over NAT by allowing DNS/UDP in the subnet NACL
# This value is optional now; the stack auto-derives the NACL from the JMeter subnet
# jmeter_subnet_network_acl_id = "acl-05cc0dd5f0abf13f2"
# Optional overrides (defaults are fine, shown here for clarity)
# ssm_nacl_rule_base_number   = 902   # will use 902/903 and 904 if NTP enabled
# ssm_nacl_enable_ntp         = true  # allow UDP 123 egress for time sync
# ssm_nacl_ingress_cidr       = "0.0.0.0/0"  # scope to VPC CIDR if preferred
