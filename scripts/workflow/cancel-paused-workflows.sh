#! /bin/bash

# fail on first error
set -e
# This script identifies workflows that have been paused for more than the specified number of days
# and cancels them if they exceed the threshold.
# Usage: ./cancel-paused-workflows.sh <REPO> [THRESHOLD_DAYS] [MAX_RUNS]

EXPORTS_SET=0

if [ -z "$REPO" ] ; then
    echo REPO not set
    EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more parameters not set
  exit 1
fi

export THRESHOLD_DAYS="${THRESHOLD_DAYS:-1}"  # Default to 24 hours if not set
export MAX_RUNS="${MAX_RUNS:-100}"  # Default to 100 runs if not set

THRESHOLD_SECONDS=$((THRESHOLD_DAYS * 24 * 60 * 60))  # Convert days to seconds
echo "Review a maximum of $MAX_RUNS workflows in repository $REPO that are waiting more than $THRESHOLD_SECONDS seconds since they were started "

NOW=$(date +%s) # Current time in seconds since epoch

runs="$(gh run list --status "waiting" --repo "$REPO" --limit "$MAX_RUNS" --json databaseId,status,createdAt,displayTitle,name)"

for run in $(echo "${runs}" | jq -r '.[] | @base64'); do
    _jq() {
      echo ${run} | base64 --decode | jq -r ${1}
    }

    ID=$( _jq '.databaseId')
    TITLE=$( _jq  '.displayTitle')
    CREATED_AT=$( _jq '.createdAt')
    echo "Processing workflow ID: $ID, Title: $TITLE, Created At: $CREATED_AT"

    # Convert createdAt to seconds since epoch
    CREATED_AT_SECONDS=$(date -d "$CREATED_AT" +%s)

    if [[ -z "$CREATED_AT_SECONDS" ]]; then
      echo "Error: Unable to parse createdAt for workflow $ID. Please check the date format."
      continue
    fi

    AGE_IN_SECONDS=$((NOW - CREATED_AT_SECONDS))

    if (( AGE_IN_SECONDS > THRESHOLD_SECONDS )); then
      echo "Cancelling workflow $ID ($TITLE) which has been paused for more than $THRESHOLD_DAYS days."
      gh run cancel "$ID" --repo "$REPO"
    else
      echo "Workflow $ID ($TITLE) has been paused for $AGE_IN_SECONDS seconds, which is below the threshold of $THRESHOLD_SECONDS seconds ($THRESHOLD_DAYS days)."
    fi
done

echo "Script completed successfully."
