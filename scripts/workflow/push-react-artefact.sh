#!/bin/bash

# fail on first error
set -e

export ARTEFACT_BUCKET_NAME="${ARTEFACT_BUCKET_NAME:-""}"
export WORKSPACE="${WORKSPACE:-""}"
export COMMIT_HASH="${COMMIT_HASH:-""}"
export FRONT_END_DIR="${FRONT_END_DIR:-"src/frontend"}"
export DEPLOYMENT_FILE_NAME="build.zip"

# check exports have been done
EXPORTS_SET=0
# Check key variables have been exported - see above

if [ -z "$FRONT_END_DIR" ] ; then
  echo Set FRONT_END_DIR to name of the front end directory
  EXPORTS_SET=1
fi

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

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not sets
  exit 1
fi

echo "Push to S3 bucket: $ARTEFACT_BUCKET_NAME"
echo "Workspace: $WORKSPACE"
echo "Commit Hash: $COMMIT_HASH"
echo "Front end directory: $FRONT_END_DIR"

# Push artefacts to s3 bucket

  cd "$FRONT_END_DIR/build"
  zip -r ../build.zip .
  cd ..
  aws s3 cp build.zip s3://$ARTEFACT_BUCKET_NAME/$WORKSPACE/$COMMIT_HASH/$DEPLOYMENT_FILE_NAME

  echo "Push to S3 bucket completed"
