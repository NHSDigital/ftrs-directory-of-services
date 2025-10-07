locals {
  rds_secret = jsondecode(data.aws_secretsmanager_secret_version.replica_rds.secret_string)
}

module "athena_output_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${local.resource_prefix}-athena-output"

  lifecycle_rule_inputs = [
    {
      id      = "delete_logs_older_than_x_days"
      enabled = true
      filter = {
        prefix = ""
      }
      expiration = {
        days = var.athena_output_bucket_retention_days
      }
    }
  ]
}

resource "aws_glue_catalog_database" "athena_glue_catalog_database" {
  name = "${local.resource_prefix}-athena-db"
}

resource "aws_athena_workgroup" "athena_workgroup" {
  name = "${local.resource_prefix}-athena-workgroup"
  configuration {
    result_configuration {
      output_location = "s3://${module.athena_output_bucket.s3_bucket_id}/results/"
    }
  }
}

# Athena Federated Query (DynamoDB Connector)
# Use this approach if you require real-time querying of DynamoDB tables via Athena.

module "athena_spill_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${local.resource_prefix}-athena-spill"

  force_destroy = true
  lifecycle_rule_inputs = [
    {
      id      = "delete_logs_older_than_x_days"
      enabled = true
      filter = {
        prefix = ""
      }
      expiration = {
        days = var.athena_spill_bucket_retention_days
      }
    }
  ]
}

resource "aws_serverlessapplicationrepository_cloudformation_stack" "dynamodb_connector" {
  name           = "${local.resource_prefix}-athena-dynamodb-connector"
  application_id = var.athena_dynamodb_connector_app_id

  capabilities = [
    "CAPABILITY_IAM",
    "CAPABILITY_RESOURCE_POLICY",
  ]

  parameters = {
    AthenaCatalogName = "${local.resource_prefix}-athena-dynamodb-connector"
    SpillBucket       = module.athena_spill_bucket.s3_bucket_id
    LambdaRole        = aws_iam_role.athena_dynamodb_role.arn
  }

  depends_on = [
    aws_iam_role.athena_dynamodb_role,
    aws_iam_role_policy.athena_dynamodb_policy,
    module.athena_spill_bucket
  ]
}

resource "aws_athena_data_catalog" "dynamodb" {
  name        = "${local.resource_prefix}-athena-dynamodb-connector"
  description = "Athena dynamodb data catalog"
  type        = "LAMBDA"

  parameters = {
    "function" = data.aws_lambda_function.dynamodb_lambda_connector.arn
  }
}

# Athena Federated Query (RDS Connector)
# Use this approach if you require real-time querying of RDS databases via Athena.

resource "aws_serverlessapplicationrepository_cloudformation_stack" "rds_connector" {
  name           = "${local.resource_prefix}-rds-connector"
  application_id = var.athena_postgres_connector_app_id

  capabilities = [
    "CAPABILITY_IAM",
    "CAPABILITY_AUTO_EXPAND",
  ]

  parameters = {
    DatabaseEngine               = "aurora-postgresql"
    ConnectionString             = "jdbc:postgresql://${local.rds_secret.host}:${local.rds_secret.port}/${local.rds_secret.dbname}"
    SecretArn                    = data.aws_secretsmanager_secret.replica_rds.arn
    OutputBucket                 = aws_s3_bucket.athena_output.bucket
    AthenaWorkGroup              = aws_athena_workgroup.main.name
    LambdaFunctionName           = "${local.resource_prefix}-athena-postgres-connector"
    SecurityGroupIds             = join(",", [aws_security_group.rds_security_group.id])
    SubnetIds                    = join(",", data.aws_subnets.private_subnets.ids)
    LogLevel                     = "INFO"
    EnableGlueCrawlerIntegration = "true"
    GlueDatabaseName             = aws_glue_catalog_database.athena_db.name
  }
}
