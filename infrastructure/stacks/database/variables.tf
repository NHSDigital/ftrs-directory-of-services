variable "dynamodb_tables" {
  description = "List of DynamoDB tables"
  type = map(object({
    hash_key  = string
    range_key = string
    attributes = list(object({
      name = string
      type = string
    }))
    global_secondary_indexes = optional(list(object({
      name               = string
      hash_key           = string
      range_key          = optional(string)
      projection_type    = string
      non_key_attributes = optional(list(string))
    })))
  }))
}
