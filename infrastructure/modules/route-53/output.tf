output "zone_id" {
  description = "The ID of the created hosted zone"
  value       = aws_route53_zone.cm.zone_id
}

output "zone_name" {
  description = "The name of the created hosted zone"
  value       = aws_route53_zone.cm.name
}
