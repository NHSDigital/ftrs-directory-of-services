#!/bin/bash
set -e

exit_code=0

function check_git_branch_name {
    BRANCH=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    VALID_FORMAT=$(check_git_branch_name_format "$BRANCH")
    if [[  ! -z "$VALID_FORMAT" ]] ; then
      echo "Branch name $1 does not match the naming pattern"
      echo Naming pattern = task or hotfix/hyphenated JIRA ref followed by underscore or hyphen followed by max 45 alphanumerics, hyphens or underscores starting with an alphanumeric
      return 1
    fi
}

function check_git_branch_name_format {
    BUILD_BRANCH="$1"
    if [ "$BUILD_BRANCH" != 'main' ] && ! [[ $BUILD_BRANCH =~ (hotfix|task)\/(fdos|dosis|sia)-([0-9]{1,5})(_|-)([A-Za-z0-9])([A-Za-z0-9_-]{9,45})$ ]]  ; then
      echo 1
    fi
}

BRANCH_NAME=${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}
check_git_branch_name "$BRANCH_NAME"

[ $? != 0 ] && exit_code=1 ||:
exit $exit_code
