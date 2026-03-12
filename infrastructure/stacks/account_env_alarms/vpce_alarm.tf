module "vpce_alarms" {
  count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix = local.resource_prefix

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "VPC Endpoint Alarms"
  kms_key_id       = data.aws_kms_key.sns_kms_key[0].arn

  alarm_config_path = "vpce/config"

  monitored_resources = {
    dynamodb_vpce        = data.aws_vpc_endpoint.dynamodb_vpce.id
    s3_vpce              = data.aws_vpc_endpoint.s3_vpce.id
    current_dos_rds_vpce = data.aws_vpc_endpoint.current_dos_rds_endpoint.id
    sqs_vpce             = data.aws_vpc_endpoint.sqs_vpce.id
    ssm_vpce             = data.aws_vpc_endpoint.ssm_vpce.id
    ssmmessages_vpce     = data.aws_vpc_endpoint.ssmmessages_vpce.id
    ec2messages_vpce     = data.aws_vpc_endpoint.ec2messages_vpce.id
    kms_vpce             = data.aws_vpc_endpoint.kms_vpce.id
    secretsmanager_vpce  = data.aws_vpc_endpoint.secretsmanager_vpce.id
    rds_vpce             = data.aws_vpc_endpoint.rds_vpce.id
    appconfig_vpce       = data.aws_vpc_endpoint.appconfig_vpce.id
    appconfigdata_vpce   = data.aws_vpc_endpoint.appconfigdata_vpce.id
    lambda_vpce          = data.aws_vpc_endpoint.lambda_vpce.id
    logs_vpce            = data.aws_vpc_endpoint.logs_vpce.id
  }

  resource_metadata = {}

  resource_additional_dimensions = {
    dynamodb_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.dynamodb_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.dynamodb_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    s3_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.s3_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.s3_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    current_dos_rds_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.current_dos_rds_endpoint.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.current_dos_rds_endpoint.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    sqs_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.sqs_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.sqs_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    ssm_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.ssm_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.ssm_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    ssmmessages_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.ssmmessages_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.ssmmessages_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    ec2messages_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.ec2messages_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.ec2messages_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    kms_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.kms_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.kms_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    secretsmanager_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.secretsmanager_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.secretsmanager_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    rds_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.rds_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.rds_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    appconfig_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.appconfig_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.appconfig_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    appconfigdata_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.appconfigdata_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.appconfigdata_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    lambda_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.lambda_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.lambda_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
    }
    logs_vpce = {
      "Endpoint Type" = data.aws_vpc_endpoint.logs_vpce.vpc_endpoint_type
      "Service Name"  = data.aws_vpc_endpoint.logs_vpce.service_name
      "VPC Id"        = data.aws_vpc.vpc.id
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

  slack_notifier_function_name = local.slack_notifier_function_name

  tags = {
    Name = "${local.resource_prefix}-vpce-alarms"
  }
}
