# S3 alarms: truststore bucket
truststore_s3_5xx_errors_warning_alarm_threshold           = 1
truststore_s3_5xx_errors_critical_alarm_threshold          = 5
truststore_s3_4xx_errors_warning_alarm_threshold           = 25
truststore_s3_4xx_errors_critical_alarm_threshold          = 50
truststore_s3_5xx_errors_warning_alarm_evaluation_periods  = 1
truststore_s3_5xx_errors_critical_alarm_evaluation_periods = 1
truststore_s3_4xx_errors_warning_alarm_evaluation_periods  = 1
truststore_s3_4xx_errors_critical_alarm_evaluation_periods = 1
truststore_s3_5xx_errors_warning_alarm_period              = 300
truststore_s3_5xx_errors_critical_alarm_period             = 300
truststore_s3_4xx_errors_warning_alarm_period              = 300
truststore_s3_4xx_errors_critical_alarm_period             = 300

# S3 alarms: Terraform state bucket
terraform_state_s3_5xx_errors_warning_alarm_threshold           = 1
terraform_state_s3_5xx_errors_critical_alarm_threshold          = 5
terraform_state_s3_4xx_errors_warning_alarm_threshold           = 25
terraform_state_s3_4xx_errors_critical_alarm_threshold          = 50
terraform_state_s3_5xx_errors_warning_alarm_evaluation_periods  = 1
terraform_state_s3_5xx_errors_critical_alarm_evaluation_periods = 1
terraform_state_s3_4xx_errors_warning_alarm_evaluation_periods  = 1
terraform_state_s3_4xx_errors_critical_alarm_evaluation_periods = 1
terraform_state_s3_5xx_errors_warning_alarm_period              = 300
terraform_state_s3_5xx_errors_critical_alarm_period             = 300
terraform_state_s3_4xx_errors_warning_alarm_period              = 300
terraform_state_s3_4xx_errors_critical_alarm_period             = 300

# VPC Endpoint alarms (shared thresholds applied to all VPC endpoints)
vpce_active_connections_warning_alarm_threshold           = 1
vpce_active_connections_critical_alarm_threshold          = 0
vpce_active_connections_warning_alarm_evaluation_periods  = 1
vpce_active_connections_critical_alarm_evaluation_periods = 1
vpce_active_connections_warning_alarm_period              = 300
vpce_active_connections_critical_alarm_period             = 300

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
