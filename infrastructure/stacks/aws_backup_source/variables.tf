variable "backup_selection_tag" {
  description = "Tag used by AWS Backup to select resources."
  type        = string
  default     = "NHSE-Enable-Backup"
}

variable "backup_daily_schedule" {
  description = "Cron schedule for daily backups."
  type        = string
  default     = "cron(0 0 * * ? *)"
}

variable "backup_weekly_schedule" {
  description = "Cron schedule for weekly backups."
  type        = string
  default     = "cron(0 1 ? * SUN *)"
}

variable "backup_monthly_schedule" {
  description = "Cron schedule for monthly backups."
  type        = string
  default     = "cron(0 2 1 * ? *)"
}

variable "backup_point_in_time_schedule" {
  description = "Cron schedule for point-in-time recovery backups."
  type        = string
  default     = "cron(0 5 * * ? *)"
}

variable "backup_source_daily_retention_days" {
  description = "Retention days for daily backups in the source account."
  type        = number
  default     = 35
}

variable "backup_source_weekly_retention_days" {
  description = "Retention days for weekly backups in the source account."
  type        = number
  default     = 90
}

variable "backup_source_monthly_retention_days" {
  description = "Retention days for monthly backups in the source account."
  type        = number
  default     = 2555
}

variable "backup_source_monthly_cold_storage_after_days" {
  description = "Cold storage transition days for monthly backups in the source account."
  type        = number
  default     = 30
}

variable "backup_source_pitr_retention_days" {
  description = "Retention days for point-in-time recovery backups in the source account."
  type        = number
  default     = 35
}

variable "backup_destination_retention_days" {
  description = "Retention days for copies stored in the destination account."
  type        = number
  default     = 365
}

variable "backup_destination_enable_vault_protection" {
  description = "Enable destination vault lock protection."
  type        = bool
  default     = false
}

variable "backup_destination_vault_lock_type" {
  description = "Destination vault lock type (governance or compliance)."
  type        = string
  default     = "governance"
}

variable "backup_destination_vault_lock_min_retention_days" {
  description = "Minimum retention days enforced by destination vault lock."
  type        = number
  default     = 365
}

variable "backup_destination_vault_lock_max_retention_days" {
  description = "Maximum retention days enforced by destination vault lock."
  type        = number
  default     = 365
}

variable "backup_destination_changeable_for_days" {
  description = "Days the destination vault lock can be modified (compliance only)."
  type        = number
  default     = 14
}

variable "restore_testing_enabled" {
  description = "Enable AWS Backup restore testing resources."
  type        = bool
  default     = true
}

variable "backup_report_bucket_retention_days" {
  description = "Retention days for backup report bucket objects."
  type        = number
  default     = 90
}