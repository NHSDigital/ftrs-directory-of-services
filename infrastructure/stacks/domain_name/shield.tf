module "shield_protection_domain" {
  source = "../../modules/shield"

  providers = {
    aws = aws.us-east-1
  }

  arn_to_protect = var.environment == "mgmt" ? aws_route53_zone.root_zone[0].arn : aws_route53_zone.environment_zone[0].arn

  health_check_association_arn       = ""
  resource_name                      = var.environment == "mgmt" ? "route53-mgmt-root-domain" : "route53-env-domain"
  resource_prefix                    = local.resource_prefix
  alarm_notification_email           = var.alarm_notification_email
  emergency_contacts                 = var.emergency_contacts
  isShieldProactiveEngagementEnabled = var.isShieldProactiveEngagementEnabled
  isShieldSRTAccessEnabled           = var.isShieldSRTAccessEnabled
  isShieldAutomaticResponseEnabled   = var.isShieldAutomaticResponseEnabled

  depends_on = flatten([var.environment == "mgmt" ? [aws_route53_zone.root_zone] : [aws_route53_zone.environment_zone]])
}
