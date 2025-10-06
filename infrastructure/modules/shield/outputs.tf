output "shield_protection_arns" {
  description = "The ARNs of the shield protection"
  value       = aws_shield_protection.shield_advanced_protection.arn
}
