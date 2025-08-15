#! /bin/bash

# This script monitors an AWS SQS queue for pending messages in the specified environment.
# It continuously polls the queue at regular intervals until there are no messages left
# (including delayed or not visible ones), at which point it exits.

# Fail on first error
set -e

export ENV="${ENV:-dev}"

# Check required environment variable
if [ -z "$QUEUE_NAME" ] ; then
  echo "ERROR: QUEUE_NAME is not set. Please export QUEUE_NAME to the name of the SQS queue to poll."
  exit 1
fi

# Initialize counts
message_num=0
delayed_num=0
not_visible_num=0

# Attributes to pull back from SQS
num_messages_attr="ApproximateNumberOfMessages"
num_delayed_attr="ApproximateNumberOfMessagesDelayed"
num_not_visible_attr="ApproximateNumberOfMessagesNotVisible"

poll_queue=1
pause_in_seconds=30

echo "Pausing 60 seconds to allow the queue to populate with messages..."
sleep 60

# Find the SQS queue URL for the environment
queue_url=$(aws sqs get-queue-url --queue-name "$QUEUE_NAME" | jq -r '.QueueUrl' 2>&1)

# Poll the queue until empty
while [ $poll_queue -eq 1 ]; do
  echo "Polling SQS queue $queue_url in $ENV environment every $pause_in_seconds seconds for messages..."
  message_numbers=$(aws sqs get-queue-attributes \
  --queue-url "$queue_url" \
  --attribute-names $num_messages_attr $num_delayed_attr $num_not_visible_attr 2>&1)

  message_num=$(echo "$message_numbers" | jq -r '.Attributes.ApproximateNumberOfMessages')
  delayed_num=$(echo "$message_numbers" | jq -r '.Attributes.ApproximateNumberOfMessagesDelayed')
  not_visible_num=$(echo "$message_numbers" | jq -r '.Attributes.ApproximateNumberOfMessagesNotVisible')

  echo "Number of messages in queue: $message_num"
  echo "Number of delayed messages in queue: $delayed_num"
  echo "Number of not visible messages in queue: $not_visible_num"

  if [ "$message_num" -eq 0 ] && [ "$delayed_num" -eq 0 ] && [ "$not_visible_num" -eq 0 ]; then
    echo "No messages in queue, exiting..."
    poll_queue=0
    continue
  else
    echo "Sleeping for $pause_in_seconds seconds before next poll..."
    sleep "$pause_in_seconds"
  fi
done

echo "Finished polling "$QUEUE_NAME" queue in $ENV"
