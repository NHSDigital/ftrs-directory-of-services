#! /bin/bash

# fail on first error
set -e
EXPORTS_SET=0

# check necessary environment variables are set
if [ -z "$WORKSPACE" ] ; then
  echo Set WORKSPACE
  EXPORTS_SET=1
fi

if [ -z "$ARTEFACT_BUCKET_NAME" ] ; then
  echo Set ARTEFACT_BUCKET_NAME
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

if [ "$WORKSPACE" == "default" ] ; then
  echo WORKSPACE can not be default
  exit 1
fi

ARTEFACT_DEVELOPMENT_PATH=$ARTEFACT_BUCKET_NAME/development/$WORKSPACE
echo "Clearing down artefacts at or below $ARTEFACT_DEVELOPMENT_PATH"

deletion_output=$(aws s3 rm --recursive s3://$ARTEFACT_DEVELOPMENT_PATH 2>&1)

if [ -n "$deletion_output" ]; then
  echo "Sucessfully deleted following artefacts from $ARTEFACT_DEVELOPMENT_PATH"
  echo "$deletion_output"
else
  echo "Problem deleting artefacts at $ARTEFACT_DEVELOPMENT_PATH. Does targetted folder exist?"
  echo "$deletion_output"
fi
