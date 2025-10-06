s3_versioning                      = true
read_only_viewer_bucket_name       = "frontend-bucket"
read_only_viewer_cloud_front_name  = "frontend-cf"
frontend_lambda_name               = "frontend-lambda"
frontend_lambda_connection_timeout = 30
frontend_lambda_memory_size        = 256
waf_name                           = "frontend-waf-web-acl"
waf_scope                          = "CLOUDFRONT"

# CloudFront Real-time Metrics
realtime_metrics_subscription_status = "Enabled" #Options are Enabled or Disabled
create_monitoring_subscription       = true

#Shield Configurations
isShieldProactiveEngagementEnabled = false
isShieldSRTAccessEnabled           = false
isShieldAutomaticResponseEnabled   = true
alarm_notification_email           = []
emergency_contacts                 = []
