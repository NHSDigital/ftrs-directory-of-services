variable "dynamodb_tables" {
  description = "List of DynamoDB tables"
  type = map(object({
    hash_key  = string
    range_key = string
    attributes = list(object({
      name = string
      type = string
    }))
  }))
}
