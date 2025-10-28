s3_versioning                = true
ui_bucket_name               = "frontend-bucket"
ui_lambda_name               = "frontend-lambda"
ui_lambda_connection_timeout = 30
ui_lambda_memory_size        = 256
waf_name                     = "frontend-waf-web-acl"
waf_scope                    = "CLOUDFRONT"

# CloudFront Real-time Metrics
realtime_metrics_subscription_status = "Enabled" #Options are Enabled or Disabled
create_monitoring_subscription       = true

#Shield Configurations
isShieldProactiveEngagementEnabled = false
isShieldSRTAccessEnabled           = false
isShieldAutomaticResponseEnabled   = true
alarm_notification_email           = []
emergency_contacts                 = []

http_version             = "http2and3"
origin_protocol_policy   = "https-only"
origin_ssl_protocols     = ["TLSv1.2"]
ssl_support_method       = "sni-only"
minimum_protocol_version = "TLSv1.2_2021"
