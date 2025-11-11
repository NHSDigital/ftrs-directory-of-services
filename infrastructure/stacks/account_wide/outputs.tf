# // Centralized outputs for the account_wide stack

# output "performance_instance_id" {
#   description = "ID of the Performance EC2 instance"
#   value       = aws_instance.performance.id
# }

# output "performance_private_ip" {
#   description = "Private IP of the Performance EC2 instance"
#   value       = aws_instance.performance.private_ip
# }

# output "performance_security_group_id" {
#   description = "Security group ID for the Performance instance"
#   value       = aws_security_group.performance_ec2_sg.id
# }

# output "performance_parameter_bucket_name" {
#   description = "Resolved S3 bucket name for Performance files"
#   value       = local.performance_files_bucket_name
# }


# output "performance_secret_api_jmeter_pks_key_arn" {
#   description = "ARN of the API JMeter PKS key secret used by Performance EC2"
#   value       = aws_secretsmanager_secret.api_jmeter_pks_key.arn
# }

# output "performance_secret_api_ca_cert_arn" {
#   description = "ARN of the API CA certificate secret used by Performance EC2"
#   value       = aws_secretsmanager_secret.api_ca_cert.arn
# }

# output "performance_secret_api_ca_pk_arn" {
#   description = "ARN of the API CA private key secret used by Performance EC2"
#   value       = aws_secretsmanager_secret.api_ca_pk.arn
# }
