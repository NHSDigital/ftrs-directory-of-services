resource "aws_glue_catalog_database" "athena_glue_catalog_database" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  name = "${local.resource_prefix}-glue-db"
}

resource "aws_athena_workgroup" "athena_workgroup" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  name = "${local.resource_prefix}-workgroup"
  configuration {
    result_configuration {
      output_location = "s3://${module.athena_output_bucket[0].s3_bucket_id}/results/"
      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key_arn       = data.aws_kms_key.athena_kms_key[0].arn
      }
    }
  }
}

# # Athena Federated Query (DynamoDB Connector)
# # Use this approach if you require real-time querying of DynamoDB tables via Athena.

# resource "aws_serverlessapplicationrepository_cloudformation_stack" "dynamodb_connector" {
#   count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

#   name           = "${local.resource_prefix}-dynamodb-connector"
#   application_id = var.athena_dynamodb_connector_app_id

#   capabilities = [
#     "CAPABILITY_IAM",
#     "CAPABILITY_RESOURCE_POLICY",
#   ]

#   parameters = {
#     AthenaCatalogName = "${local.resource_prefix}-dynamodb-connector"
#     SpillBucket       = module.athena_spill_bucket[0].s3_bucket_id
#     LambdaRole        = aws_iam_role.athena_dynamodb_role[0].arn
#   }

#   depends_on = [
#     module.athena_spill_bucket,
#     aws_iam_role.athena_dynamodb_role,
#     aws_iam_role_policy.athena_dynamodb_policy
#   ]
# }

# resource "aws_athena_data_catalog" "athena_data_catalog_dynamodb" {
#   count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

#   name        = "${local.resource_prefix}-dynamodb-connector"
#   description = "Athena DynamoDB data catalog"
#   type        = "LAMBDA"

#   parameters = {
#     "function" = data.aws_lambda_function.dynamodb_lambda_connector[0].arn
#   }

#   depends_on = [
#     aws_serverlessapplicationrepository_cloudformation_stack.dynamodb_connector
#   ]
# }

# Athena Federated Query (RDS Connector)
# Use this approach if you require real-time querying of RDS databases via Athena.

# resource "aws_serverlessapplicationrepository_cloudformation_stack" "rds_connector" {
#   count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

#   name           = "${local.resource_prefix}-rds-connector"
#   application_id = var.athena_postgres_connector_app_id

#   capabilities = [
#     "CAPABILITY_IAM",
#     "CAPABILITY_AUTO_EXPAND",
#     "CAPABILITY_RESOURCE_POLICY",
#   ]

#   parameters = {
#     SpillBucket             = module.athena_spill_bucket[0].s3_bucket_id
#     DefaultConnectionString = "postgres://jdbc:postgresql://${local.rds_secret.host}:${local.rds_secret.port}/${local.rds_secret.dbname}?$${${data.aws_secretsmanager_secret.target_rds_credentials[0].name}}"
#     SecretNamePrefix        = "/${var.project}/${var.environment}/${var.target_rds_credentials}"
#     LambdaFunctionName      = "${local.resource_prefix}-rds-connector"
#     SecurityGroupIds        = data.aws_security_group.athena_rds_connector_sg[0].id
#     SubnetIds               = join(",", data.aws_subnets.private_subnets.ids)
#   }

#   depends_on = [
#     module.athena_spill_bucket
#   ]
# }

# resource "aws_athena_data_catalog" "athena_data_catalog_rds" {
#   count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

#   name        = "${local.resource_prefix}-rds-connector"
#   description = "Athena RDS data catalog"
#   type        = "LAMBDA"

#   parameters = {
#     "function" = data.aws_lambda_function.rds_lambda_connector[0].arn
#   }

#   depends_on = [
#     aws_serverlessapplicationrepository_cloudformation_stack.rds_connector
#   ]
# }
