// Optional Network ACL rules to support SSM over NAT by allowing DNS and UDP return traffic.
// These are only created when var.jmeter_subnet_network_acl_id is provided, or when one can be derived from the JMeter subnet.

// Derive the Network ACL associated with the chosen JMeter subnet (local.jmeter_subnet_id)
data "aws_network_acls" "jmeter_for_subnet" {
  filter {
    name   = "association.subnet-id"
    values = [local.jmeter_subnet_id]
  }
}

locals {
  // Prefer explicit variable if set; otherwise use the first NACL associated with the subnet (if any)
  derived_jmeter_nacl_id        = length(data.aws_network_acls.jmeter_for_subnet.ids) > 0 ? data.aws_network_acls.jmeter_for_subnet.ids[0] : null
  effective_jmeter_nacl_id      = var.jmeter_subnet_network_acl_id != "" ? var.jmeter_subnet_network_acl_id : local.derived_jmeter_nacl_id
  have_effective_jmeter_nacl_id = local.effective_jmeter_nacl_id != null && local.effective_jmeter_nacl_id != ""
}

resource "aws_network_acl_rule" "jmeter_dns_egress_udp_53" {
  count          = local.have_effective_jmeter_nacl_id ? 1 : 0
  network_acl_id = local.effective_jmeter_nacl_id
  egress         = true
  rule_number    = var.ssm_nacl_rule_base_number
  protocol       = "udp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 53
  to_port        = 53
}

resource "aws_network_acl_rule" "jmeter_udp_ephemeral_ingress" {
  count          = local.have_effective_jmeter_nacl_id ? 1 : 0
  network_acl_id = local.effective_jmeter_nacl_id
  egress         = false
  rule_number    = var.ssm_nacl_rule_base_number + 1
  protocol       = "udp"
  rule_action    = "allow"
  cidr_block     = var.ssm_nacl_ingress_cidr
  from_port      = 1024
  to_port        = 65535
}

resource "aws_network_acl_rule" "jmeter_ntp_egress_udp_123" {
  count          = (local.have_effective_jmeter_nacl_id && var.ssm_nacl_enable_ntp) ? 1 : 0
  network_acl_id = local.effective_jmeter_nacl_id
  egress         = true
  rule_number    = var.ssm_nacl_rule_base_number + 2
  protocol       = "udp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 123
  to_port        = 123
}
