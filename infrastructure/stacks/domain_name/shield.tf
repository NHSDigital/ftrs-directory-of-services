module "shield_protection_mgmt_root_domain" {
  count  = var.environment == "mgmt" && local.is_primary_environment ? 1 : 0
  source = "../../modules/shield"

  providers = {
    aws = aws.us-east-1
  }

  arn_to_protect                     = aws_route53_zone.root_zone[0].arn
  health_check_association_arn       = ""
  distribution_id_to_protect         = ""
  resource_name                      = "route53-mgmt-root-domain"
  resource_prefix                    = local.resource_prefix
  alarm_notification_email           = var.alarm_notification_email
  emergency_contacts                 = var.emergency_contacts
  isShieldProactiveEngagementEnabled = var.isShieldProactiveEngagementEnabled
  isShieldSRTAccessEnabled           = var.isShieldSRTAccessEnabled
  isShieldAutomaticResponseEnabled   = var.isShieldAutomaticResponseEnabled

  depends_on = [aws_route53_zone.root_zone]
}

module "shield_protection_env_domain" {
  count  = var.environment == "mgmt" && local.is_primary_environment ? 0 : 1
  source = "../../modules/shield"

  providers = {
    aws = aws.us-east-1
  }

  arn_to_protect                     = aws_route53_zone.environment_zone[0].arn
  health_check_association_arn       = ""
  distribution_id_to_protect         = ""
  resource_name                      = "route53-env-domain"
  resource_prefix                    = local.resource_prefix
  alarm_notification_email           = var.alarm_notification_email
  emergency_contacts                 = var.emergency_contacts
  isShieldProactiveEngagementEnabled = var.isShieldProactiveEngagementEnabled
  isShieldSRTAccessEnabled           = var.isShieldSRTAccessEnabled
  isShieldAutomaticResponseEnabled   = var.isShieldAutomaticResponseEnabled

  depends_on = [aws_route53_zone.environment_zone]
}
