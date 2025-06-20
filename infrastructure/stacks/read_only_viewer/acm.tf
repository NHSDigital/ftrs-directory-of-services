module "cloudfront_certificate" {
  # Module version: v5.2.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-acm.git?ref=61c702b3ad1635ebeb997bfa683eb1a17813bfd8"

  providers = {
    aws = aws.us-east-1
  }

  domain_name         = "viewer.${var.domain_name}"
  zone_id             = data.aws_route53_zone.environment_zone.zone_id
  validation_method   = "DNS"
  wait_for_validation = true
}
