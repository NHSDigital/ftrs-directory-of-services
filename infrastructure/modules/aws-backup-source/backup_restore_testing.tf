resource "aws_backup_restore_testing_plan" "backup_restore_testing_plan" {
  count               = var.restore_testing_enabled ? 1 : 0
  name                = replace("${var.resource_prefix}_restore_plan", "-", "_")
  schedule_expression = var.restore_testing_plan_scheduled_expression
  start_window_hours  = var.restore_testing_plan_start_window

  recovery_point_selection {
    algorithm             = var.restore_testing_plan_algorithm
    include_vaults        = [aws_backup_vault.main.arn]
    recovery_point_types  = var.restore_testing_plan_recovery_point_types
    selection_window_days = var.restore_testing_plan_selection_window_days
  }
}

resource "aws_backup_restore_testing_selection" "backup_restore_testing_selection_dynamodb" {
  count                     = var.restore_testing_enabled && var.backup_plan_config_dynamodb.enable ? 1 : 0
  iam_role_arn              = aws_iam_role.backup.arn
  protected_resource_type   = "DynamoDB"
  restore_testing_plan_name = aws_backup_restore_testing_plan.backup_restore_testing_plan[0].name
  name                      = replace("${var.resource_prefix}_ddb_sel", "-", "_")

  protected_resource_conditions {
    string_equals {
      key   = "aws:ResourceTag/${var.backup_plan_config_dynamodb.selection_tag}"
      value = var.environment_name
    }
  }
}
