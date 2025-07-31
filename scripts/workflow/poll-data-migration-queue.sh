#! /bin/bash

# fail on first error
set -e

export ENV="${ENV:-dev}"
export QUEUE_NAME="${QUEUE_NAME:-ftrs-dos-${ENV}-data-migration-rds-events}"

# reset counts at start
message_num=0
delayed_num=0
not_visible_num=0

# attributes to pull back from SQS
num_messages_attr="ApproximateNumberOfMessages"
num_delayed_attr="ApproximateNumberOfMessagesDelayed"
num_not_visible_attr="ApproximateNumberOfMessagesNotVisible"

poll_queue=1
pause_in_seconds=30

# give time for lambda to start up
sleep "$pause_in_seconds"

# find the SQS queue URL for the environment
queue_list=$(aws sqs list-queues --queue-name-prefix "$QUEUE_NAME" 2>&1)
queue_url=$(echo "$queue_list" | jq -r '.QueueUrls[0]')

# now poll the queue for messages
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
  # if there are no messages in the queue, exit the loop
  if [ "$message_num" -eq 0 ] && [ "$delayed_num" -eq 0 ] && [ "$not_visible_num" -eq 0 ]; then
    echo "No messages in queue, exiting..."
    poll_queue=0
    continue
  else
    echo "Sleeping for $pause_in_seconds seconds before next poll..."
    sleep "$pause_in_seconds"
  fi
done

echo "Finished polling etl process queue in $ENV"

