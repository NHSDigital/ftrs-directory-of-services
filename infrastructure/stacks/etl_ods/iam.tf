resource "aws_iam_role" "ods_etl_scheduler_invoke_role" {
  name               = "${local.resource_prefix}-ods-etl-scheduler-invoke-role${local.workspace_suffix}"
  assume_role_policy = data.aws_iam_policy_document.ods_etl_scheduler_invoke_policy.json
  description        = "IAM role to allow the ODS ETL scheduler to invoke the processor lambda"
}
