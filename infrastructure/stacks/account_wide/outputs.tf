// Centralized outputs for the account_wide stack

output "performance_instance_id" {
  description = "ID of the Performance EC2 instance"
  value       = aws_instance.performance.id
}

output "performance_private_ip" {
  description = "Private IP of the Performance EC2 instance"
  value       = aws_instance.performance.private_ip
}

output "performance_security_group_id" {
  description = "Security group ID for the Performance instance"
  value       = aws_security_group.performance_ec2_sg.id
}

