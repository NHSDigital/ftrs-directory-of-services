module "shield_protection" {
  count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/shield"

  arn_to_protect                     = module.read_only_viewer_cloudfront.cloudfront_distribution_arn
  health_check_association_arn       = ""
  distribution_id_to_protect         = module.read_only_viewer_cloudfront.cloudfront_distribution_id
  resource_name                      = "cloudfront-read-only-viewer"
  alarm_notification_email           = []
  emergency_contacts                 = []
  isShieldProactiveEngagementEnabled = var.isShieldProactiveEngagementEnabled
  isShieldSRTAccessEnabled           = var.isShieldSRTAccessEnabled
  isShieldAutomaticResponseEnabled   = var.isShieldAutomaticResponseEnabled

  depends_on = [module.read_only_viewer_cloudfront]
}
