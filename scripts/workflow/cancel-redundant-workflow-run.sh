#! /bin/bash

# fail on first error
set -e
# This script identifies workflows that were triggered by the raising of a PR
#  and cancels them if they were not triggered by dependabot
# Usage: ./cancel-redundant-workflow-run.sh <REPO> <RUN_ID> <TRIGGERING_ACTION> <TRIGGERING_ACTOR>

EXPORTS_SET=0

if [ -z "$REPO" ] ; then
    echo REPO not set
    EXPORTS_SET=1
fi

if [ -z "$RUN_ID" ] ; then
    echo RUN_ID not set
    EXPORTS_SET=1
fi

if [ -z "$TRIGGERING_ACTION" ] ; then
    echo TRIGGERING_ACTION not set
    EXPORTS_SET=1
fi

if [ -z "$TRIGGERING_ACTOR" ] ; then
    echo TRIGGERING_ACTOR not set
    EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more parameters not set
  exit 1
fi
# pull_request
# 'dependabot[bot]'
echo "Checking triggering action ($TRIGGERING_ACTION) and actor ($TRIGGERING_ACTOR) for run  $RUN_ID in repository $REPO"

if [[ $TRIGGERING_ACTION == "push" && $TRIGGERING_ACTOR != 'timrickwood' ]] ; then
  echo "Cancelling workflow $ID because it was triggered by a pull request but is not for a dependabot branch"
  gh run cancel "$RUN_ID" --repo "$REPO"
fi





echo "Script completed successfully."
