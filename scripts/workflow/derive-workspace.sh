#!/bin/bash

echo "Trigger: $TRIGGER"
echo "Trigger action: $TRIGGER_ACTION"
echo "Trigger reference: $TRIGGER_REFERENCE"
echo "Trigger head reference: $TRIGGER_HEAD_REFERENCE "
echo "Trigger event reference $TRIGGER_EVENT_REF"
echo "Commit hash (for dependabot only): $COMMIT_HASH"

WORKSPACE="Unknown"

# Tags always use default workspace
if [ "$TRIGGER" == "tag" ] ; then
  WORKSPACE="default"
  echo -e "\nTag detected - using default workspace"
  echo "Workspace: $WORKSPACE"
  export WORKSPACE
  exit 0
fi

# Determine branch name based on trigger
echo -e "\nDetermining branch name from trigger action..."
case "$TRIGGER_ACTION" in
  push|workflow_dispatch)
    echo "Trigger: push or workflow_dispatch"
    BRANCH_NAME="${TRIGGER_REFERENCE:-$(git rev-parse --abbrev-ref HEAD)}"
    [ "$BRANCH_NAME" == "HEAD" ] && BRANCH_NAME="main"
    echo "Branch name set to: $BRANCH_NAME"
    ;;
  pull_request)
    echo "Trigger: pull_request"
    BRANCH_NAME="$TRIGGER_HEAD_REFERENCE"
    echo "Branch name set to: $BRANCH_NAME"
    ;;
  delete)
    echo "Trigger: delete"
    BRANCH_NAME="$TRIGGER_EVENT_REF"
    echo "Branch name set to: $BRANCH_NAME"
    ;;
  *)
    echo "Unknown trigger action: $TRIGGER_ACTION"
    ;;
esac

BRANCH_NAME=$(echo "$BRANCH_NAME" | sed 's/refs\/heads\/task/task/g; s/refs\/heads\/dependabot/dependabot/g')

# Derive workspace from branch name
echo -e "\nDeriving workspace from branch name..."
if [[ "${BRANCH_NAME:0:10}" == "dependabot" ]]; then
  echo "Dependabot branch detected"
  WORKSPACE="bot-$COMMIT_HASH"
  echo "Workspace: $WORKSPACE"
elif [[ "$BRANCH_NAME" == "main" || "$BRANCH_NAME" == "develop" ]]; then
  echo "main/develop branch detected"
  WORKSPACE="default"
  echo "Workspace: $WORKSPACE"
else
  echo "Task branch detected"
  IFS='/' read -r -a name_array <<< "$BRANCH_NAME"
  IFS='_-' read -r -a ref <<< "${name_array[1]}"
  WORKSPACE=$(echo "${ref[0]}-${ref[1]}" | tr "[:upper:]" "[:lower:]")
  echo "Workspace: $WORKSPACE"
fi

echo -e "\nFinal Results:"
echo "  Branch name: $BRANCH_NAME"
echo "  Workspace: $WORKSPACE"
export WORKSPACE
