module "s3_alarms" {
  count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix = local.resource_prefix # Used for naming SNS topic and alarms

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "S3 Account Wide Alarms"
  kms_key_id       = module.sns_encryption_key.arn

  alarm_config_path = "s3/config"

  monitored_resources = {
    truststore_s3      = module.trust_store_s3_bucket.s3_bucket_id
    terraform_state_s3 = data.aws_s3_bucket.terraform_state_bucket.id
  }

  resource_metadata = {}

  resource_additional_dimensions = {
    truststore_s3 = {
      "FilterId" = "EntireBucket"
    }
    terraform_state_s3 = {
      "FilterId" = "EntireBucket"
    }
  }

  alarm_thresholds = {
    truststore_s3 = {
      "5xx-errors-warning"  = var.truststore_s3_5xx_errors_warning_alarm_threshold
      "5xx-errors-critical" = var.truststore_s3_5xx_errors_critical_alarm_threshold
      "4xx-errors-warning"  = var.truststore_s3_4xx_errors_warning_alarm_threshold
      "4xx-errors-critical" = var.truststore_s3_4xx_errors_critical_alarm_threshold
    }
    terraform_state_s3 = {
      "5xx-errors-warning"  = var.terraform_state_s3_5xx_errors_warning_alarm_threshold
      "5xx-errors-critical" = var.terraform_state_s3_5xx_errors_critical_alarm_threshold
      "4xx-errors-warning"  = var.terraform_state_s3_4xx_errors_warning_alarm_threshold
      "4xx-errors-critical" = var.terraform_state_s3_4xx_errors_critical_alarm_threshold
    }
  }

  alarm_evaluation_periods = {
    truststore_s3 = {
      "5xx-errors-warning"  = var.truststore_s3_5xx_errors_warning_alarm_evaluation_periods
      "5xx-errors-critical" = var.truststore_s3_5xx_errors_critical_alarm_evaluation_periods
      "4xx-errors-warning"  = var.truststore_s3_4xx_errors_warning_alarm_evaluation_periods
      "4xx-errors-critical" = var.truststore_s3_4xx_errors_critical_alarm_evaluation_periods
    }
    terraform_state_s3 = {
      "5xx-errors-warning"  = var.terraform_state_s3_5xx_errors_warning_alarm_evaluation_periods
      "5xx-errors-critical" = var.terraform_state_s3_5xx_errors_critical_alarm_evaluation_periods
      "4xx-errors-warning"  = var.terraform_state_s3_4xx_errors_warning_alarm_evaluation_periods
      "4xx-errors-critical" = var.terraform_state_s3_4xx_errors_critical_alarm_evaluation_periods
    }
  }

  alarm_periods = {
    truststore_s3 = {
      "5xx-errors-warning"  = var.truststore_s3_5xx_errors_warning_alarm_period
      "5xx-errors-critical" = var.truststore_s3_5xx_errors_critical_alarm_period
      "4xx-errors-warning"  = var.truststore_s3_4xx_errors_warning_alarm_period
      "4xx-errors-critical" = var.truststore_s3_4xx_errors_critical_alarm_period
    }
    terraform_state_s3 = {
      "5xx-errors-warning"  = var.terraform_state_s3_5xx_errors_warning_alarm_period
      "5xx-errors-critical" = var.terraform_state_s3_5xx_errors_critical_alarm_period
      "4xx-errors-warning"  = var.terraform_state_s3_4xx_errors_warning_alarm_period
      "4xx-errors-critical" = var.terraform_state_s3_4xx_errors_critical_alarm_period
    }
  }

  enable_warning_alarms = var.enable_warning_alarms

  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  tags = {
    Name = local.alarms_topic_name
  }
}

module "vpce_alarms" {
  count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix = local.resource_prefix

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "VPC Endpoint Alarms"
  kms_key_id       = module.sns_encryption_key.arn

  alarm_config_path = "vpce/config"

  monitored_resources = {
    dynamodb_vpce        = aws_vpc_endpoint.dynamodb_vpce.id
    s3_vpce              = aws_vpc_endpoint.s3_vpce.id
    current_dos_rds_vpce = aws_vpc_endpoint.current_dos_rds_endpoint.id
    sqs_vpce             = aws_vpc_endpoint.interface_vpce["sqs"].id
    ssm_vpce             = aws_vpc_endpoint.interface_vpce["ssm"].id
    ssmmessages_vpce     = aws_vpc_endpoint.interface_vpce["ssmmessages"].id
    ec2messages_vpce     = aws_vpc_endpoint.interface_vpce["ec2messages"].id
    kms_vpce             = aws_vpc_endpoint.interface_vpce["kms"].id
    secretsmanager_vpce  = aws_vpc_endpoint.interface_vpce["secretsmanager"].id
    rds_vpce             = aws_vpc_endpoint.interface_vpce["rds"].id
    appconfig_vpce       = aws_vpc_endpoint.interface_vpce["appconfig"].id
    appconfigdata_vpce   = aws_vpc_endpoint.interface_vpce["appconfigdata"].id
    lambda_vpce          = aws_vpc_endpoint.interface_vpce["lambda"].id
    logs_vpce            = aws_vpc_endpoint.interface_vpce["logs"].id
  }

  resource_metadata = {}

  resource_additional_dimensions = {
    dynamodb_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.dynamodb_vpce.vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.dynamodb_vpce.service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    s3_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.s3_vpce.vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.s3_vpce.service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    current_dos_rds_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.current_dos_rds_endpoint.vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.current_dos_rds_endpoint.service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    sqs_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["sqs"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["sqs"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    ssm_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["ssm"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["ssm"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    ssmmessages_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["ssmmessages"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["ssmmessages"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    ec2messages_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["ec2messages"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["ec2messages"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    kms_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["kms"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["kms"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    secretsmanager_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["secretsmanager"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["secretsmanager"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    rds_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["rds"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["rds"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    appconfig_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["appconfig"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["appconfig"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    appconfigdata_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["appconfigdata"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["appconfigdata"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    lambda_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["lambda"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["lambda"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
    logs_vpce = {
      "Endpoint Type" = aws_vpc_endpoint.interface_vpce["logs"].vpc_endpoint_type
      "Service Name"  = aws_vpc_endpoint.interface_vpce["logs"].service_name
      "VPC Id"        = module.vpc.vpc_id
    }
  }

  alarm_thresholds = {
    dynamodb_vpce        = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    s3_vpce              = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    current_dos_rds_vpce = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    sqs_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    ssm_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    ssmmessages_vpce     = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    ec2messages_vpce     = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    kms_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    secretsmanager_vpce  = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    rds_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    appconfig_vpce       = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    appconfigdata_vpce   = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    lambda_vpce          = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
    logs_vpce            = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_threshold, "active-connections-critical" = var.vpce_active_connections_critical_alarm_threshold }
  }

  alarm_evaluation_periods = {
    dynamodb_vpce        = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    s3_vpce              = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    current_dos_rds_vpce = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    sqs_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    ssm_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    ssmmessages_vpce     = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    ec2messages_vpce     = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    kms_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    secretsmanager_vpce  = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    rds_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    appconfig_vpce       = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    appconfigdata_vpce   = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    lambda_vpce          = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
    logs_vpce            = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_evaluation_periods, "active-connections-critical" = var.vpce_active_connections_critical_alarm_evaluation_periods }
  }

  alarm_periods = {
    dynamodb_vpce        = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    s3_vpce              = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    current_dos_rds_vpce = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    sqs_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    ssm_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    ssmmessages_vpce     = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    ec2messages_vpce     = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    kms_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    secretsmanager_vpce  = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    rds_vpce             = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    appconfig_vpce       = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    appconfigdata_vpce   = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    lambda_vpce          = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
    logs_vpce            = { "active-connections-warning" = var.vpce_active_connections_warning_alarm_period, "active-connections-critical" = var.vpce_active_connections_critical_alarm_period }
  }

  enable_warning_alarms = var.enable_warning_alarms

  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  tags = {
    Name = "${local.resource_prefix}-vpce-alarms"
  }
}
