variable "queue_name" {
  description = "The name of the queue"
}

variable "delay_seconds" {
  description = "The number of seconds a message should be invisible to consumers"
}

variable "visibility_timeout_seconds" {
  description = "How long a message remains invisible to other consumers after being received by one consumer"
}

variable "max_message_size" {
  description = "The maximum size of the message"
}

variable "message_retention_seconds" {
  description = "How long the SQS queue keeps a message"
}

variable "receive_wait_time_seconds" {
  description = "Time period that a request could wait for a message to become available in the sqs queue"
}

variable "sqs_managed_sse_enabled" {
  description = "Enables Server-Side Encryption for messages stored in the queue"
}
