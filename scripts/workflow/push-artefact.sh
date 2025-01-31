#!/bin/bash

# fail on first error
set -e

export ARTEFACT_BUCKET_NAME="${ARTEFACT_BUCKET_NAME:-""}"
export WORKSPACE="${WORKSPACE:-""}"
export COMMIT_HASH="${COMMIT_HASH:-""}"
export DIRECTORY="${DIRECTORY:-""}"
export SERVICE="${SERVICE:-""}"

# check exports have been done
EXPORTS_SET=0
# Check key variables have been exported - see above

if [ -z "$COMMIT_HASH" ] ; then
  echo Set COMMIT_HASH to identify which artefacts to be deployed
  EXPORTS_SET=1
fi

if [ -z "$WORKSPACE" ] ; then
  echo Set WORKSPACE to the workspace to action the terraform in
  EXPORTS_SET=1
fi

if [ -z "$ARTEFACT_BUCKET_NAME" ] ; then
  echo Set ARTEFACT BUCKET NAME to the artefact bucket name to action the terraform in
  EXPORTS_SET=1
fi

if [ -z "$DIRECTORY" ] ; then
  echo Set DIRECTORY to identify which artefacts to be deployed
  EXPORTS_SET=1
fi

if [ -z "$SERVICE" ] ; then
  echo Set SERVICE to identify which artefacts to be deployed
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

echo "Push to S3 bucket: $ARTEFACT_BUCKET_NAME"
echo "Workspace: $WORKSPACE"
echo "Commit Hash: $COMMIT_HASH"

# Push artefacts to s3 bucket

  cd ./"${DIRECTORY}"/"${SERVICE}"
  aws s3 cp ${SERVICE}.zip s3://$ARTEFACT_BUCKET_NAME/$WORKSPACE/$COMMIT_HASH/

  echo "Push to S3 bucket completed"
