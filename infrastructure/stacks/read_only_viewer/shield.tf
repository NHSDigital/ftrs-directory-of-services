module "shield_protection" {
  count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/shield"

  providers = {
    aws = aws.us-east-1
  }

  arn_to_protect                     = module.read_only_viewer_cloudfront.cloudfront_distribution_arn
  health_check_association_arn       = aws_route53_health_check.calculated_health_check.arn
  resource_name                      = "cloudfront"
  resource_prefix                    = local.resource_prefix
  alarm_notification_email           = var.alarm_notification_email
  emergency_contacts                 = var.emergency_contacts
  isShieldProactiveEngagementEnabled = var.isShieldProactiveEngagementEnabled
  isShieldSRTAccessEnabled           = var.isShieldSRTAccessEnabled
  isShieldAutomaticResponseEnabled   = var.isShieldAutomaticResponseEnabled

  depends_on = [module.read_only_viewer_cloudfront]
}
