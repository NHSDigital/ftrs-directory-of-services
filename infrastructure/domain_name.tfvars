#Shield Configurations
isShieldProactiveEngagementEnabled = false
isShieldSRTAccessEnabled           = false
isShieldAutomaticResponseEnabled   = false
alarm_notification_email           = []
emergency_contacts                 = []

# ACM certificate expiry alarms
acm_days_to_expiry_warning_alarm_threshold           = 30
acm_days_to_expiry_critical_alarm_threshold          = 15
acm_days_to_expiry_warning_alarm_evaluation_periods  = 1
acm_days_to_expiry_critical_alarm_evaluation_periods = 1
acm_days_to_expiry_warning_alarm_period              = 86400
acm_days_to_expiry_critical_alarm_period             = 86400

# Route 53 health check
route53_health_check_failure_threshold = 3
route53_health_check_request_interval  = 30

# Route 53 health check alarms
route53_health_check_status_critical_alarm_threshold                      = 1
route53_health_check_status_critical_alarm_evaluation_periods             = 1
route53_health_check_status_critical_alarm_period                         = 60
route53_health_check_percentage_healthy_critical_alarm_threshold          = 100
route53_health_check_percentage_healthy_critical_alarm_evaluation_periods = 1
route53_health_check_percentage_healthy_critical_alarm_period             = 60

sns_topic_name = "route53-alarms"
