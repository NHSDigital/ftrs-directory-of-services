#!/bin/bash

exit_code=0

function check_jira_ref {
  BRANCH_NAME=$1
  COMMIT_MESSAGE=$2
  HYPHENATED_BRANCH_NAME="${BRANCH_NAME//_/-}"
  IFS='/' read -r -a name_array <<< "$HYPHENATED_BRANCH_NAME"
  IFS='-' read -r -a ref <<< "${name_array[1]}"
  JIRA_REF=$(echo "${ref[0]}"-"${ref[1]}")
  # Add jira ref if missing
  if [[ $COMMIT_MESSAGE != $JIRA_REF* ]] ; then
    COMMIT_MESSAGE="$JIRA_REF $COMMIT_MESSAGE"
  fi
  echo "$COMMIT_MESSAGE"
}

function check_git_commit_message {
  COMMIT_MESSAGE=$1
  VALID_FORMAT=$(check_commit_message_format "$COMMIT_MESSAGE")
  VALID_LENGTH=$(check_commit_message_length "$COMMIT_MESSAGE")
  if [[ ! -z "$VALID_LENGTH" || ! -z "$VALID_FORMAT" ]] ; then
    [[ ! -z "$VALID_FORMAT" ]] && echo $VALID_FORMAT
    [[ ! -z "$VALID_LENGTH" ]] && echo $VALID_LENGTH
    return 1
  fi
}

# does not impose max length
function check_commit_message_format {
    COMMIT_MESSAGE="$1"
    if ! [[ "$$(echo '$COMMIT_MESSAGE' | sed s/\'//g | head -1)" =~ (FDOS|DOSIS|SIA)-([0-9]{1,5})[[:space:]]([A-Za-z0-9]{1,})[[:space:]]([A-Za-z0-9]{1,})[[:space:]]([A-Za-z0-9]{1,}) ]] ; then
      echo The commit message $COMMIT_MESSAGE does not conform to the required rules
    fi
}
function check_commit_message_length {
    COMMIT_MESSAGE="$1"
    COMMIT_MESSAGE_LENGTH="$(echo $COMMIT_MESSAGE | sed s/\'//g | head -1 | wc -m)"
    if [[ "$COMMIT_MESSAGE_LENGTH" -gt $GIT_COMMIT_MESSAGE_MAX_LENGTH ]] ; then
      echo "At $COMMIT_MESSAGE_LENGTH characters the commit message exceeds limit of $GIT_COMMIT_MESSAGE_MAX_LENGTH"
    fi
}

GIT_COMMIT_MESSAGE_MAX_LENGTH=100
ORIGINAL_COMMIT_MESSAGE=${COMMIT_MESSAGE:-"$(cat $1)"}
BRANCH_NAME=${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}
COMMIT_MESSAGE=$(check_jira_ref "$BRANCH_NAME" "$ORIGINAL_COMMIT_MESSAGE")
sed -i -e "s/$ORIGINAL_COMMIT_MESSAGE/$COMMIT_MESSAGE/g" $1
check_git_commit_message "$(cat $1)"
exit_code=$?
exit $exit_code
