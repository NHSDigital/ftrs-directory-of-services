data "aws_acm_certificate" "vpn_cert" {
  domain      = "${local.prefix}-vpn"
  types       = ["IMPORTED"]
  statuses    = ["ISSUED"]
  most_recent = true
}
