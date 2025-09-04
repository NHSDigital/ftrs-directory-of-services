#! /bin/bash
echo "Trigger: $TRIGGER"
echo "Trigger action: $TRIGGER_ACTION"
echo "Trigger reference: $TRIGGER_REFERENCE"
echo "Trigger head reference: $TRIGGER_HEAD_REFERENCE "
echo "Trigger event reference $TRIGGER_EVENT_REF"
echo "Commit hash (for dependabot only): $COMMIT_HASH"

WORKSPACE="Unknown"

# If we are dealing with a tagging action, then the workspace is the name of the tag
if [ "$TRIGGER" == "tag" ] ; then
  WORKSPACE="$TRIGGER_REFERENCE"
  echo "Triggered by tagging - deriving workspace directly from tag: $TRIGGER_REFERENCE"
  echo "Workspace: $WORKSPACE"
  export WORKSPACE
  exit
fi

# If we are dealing with a push action or workflow_dispatch and the trigger is not a tag, we'll need to look at the branch name
# to derive the workspace
if [ "$TRIGGER_ACTION" == "push" ] || [ "$TRIGGER_ACTION" == "workflow_dispatch" ] ; then
  echo "Triggered by a push or workflow_dispatch - branch name is current branch"
  BRANCH_NAME="${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}"
# If trigger action is pull_request we will need to derive the workspace from the triggering head reference
elif [ "$TRIGGER_ACTION" == "pull_request" ] ; then
  echo "Triggered by a pull_request - setting branch name to trigger head ref "
  BRANCH_NAME="$TRIGGER_HEAD_REFERENCE"
# If trigger action is delete (of branch) we will need to derive the workspace from the event ref
elif [ "$TRIGGER_ACTION" == "delete" ] ; then
  echo "Triggered by a branch deletion - setting branch name to trigger event ref "
  BRANCH_NAME="$TRIGGER_EVENT_REF"
fi

echo "Branch name: $BRANCH_NAME"
BRANCH_NAME=$(echo "$BRANCH_NAME" | sed 's/refs\/heads\/task/task/g; s/refs\/heads\/dependabot/dependabot/g')

if [[ "${BRANCH_NAME:0:10}" == "dependabot" ]]; then
  # Handle dependabot branches
  WORKSPACE="bot-$COMMIT_HASH"
  echo "Workspace from dependabot branch: $WORKSPACE"
elif [[ "$BRANCH_NAME" == "main" ]]; then
  # Handle main branch
  WORKSPACE="default"
  echo "Workspace from main branch: $WORKSPACE"
elif [[ "$BRANCH_NAME" == "develop" ]]; then
  # Handle develop branch
  WORKSPACE="default"
  echo "Workspace from develop branch: $WORKSPACE"
else
  # Handle task branches
  IFS='/' read -r -a name_array <<< "$BRANCH_NAME"
  IFS='_-' read -r -a ref <<< "${name_array[1]}"
  WORKSPACE=$(echo "${ref[0]}-${ref[1]}" | tr "[:upper:]" "[:lower:]")
  echo "Workspace from feature branch: $WORKSPACE"
fi

echo "Branch name: $BRANCH_NAME"
echo "Workspace: $WORKSPACE"
export WORKSPACE
