module "shield_protection" {
  count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/shield"

  arn_to_protect                     = aws_cloudfront_distribution.read_only_viewer_distribution.arn
  health_check_association_arn       = ""
  distribution_id_to_protect         = aws_cloudfront_distribution.read_only_viewer_distribution.id
  resource_name                      = "cloudfront-read-only-viewer"
  alarm_notification_email           = []
  emergency_contacts                 = [{}]
  isShieldProactiveEngagementEnabled = var.isShieldProactiveEngagementEnabled
  isShieldSRTAccessEnabled           = var.isShieldSRTAccessEnabled
  isShieldAutomaticResponseEnabled   = var.isShieldAutomaticResponseEnabled

  depends_on = [aws_cloudfront_distribution.read_only_viewer_distribution]
}
