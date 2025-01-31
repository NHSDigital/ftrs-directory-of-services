output "rest_api_id" {
  description = "The unique id of the api gateway rest api."
  value       = resource.aws_api_gateway_rest_api.rest_api.id
}
output "root_resource_id" {
  description = "Id of resource root"
  value       = resource.aws_api_gateway_rest_api.rest_api.root_resource_id
}
