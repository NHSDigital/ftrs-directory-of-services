#!/bin/bash
export FRONT_END_DIR="${FRONT_END_DIR:-"src/frontend"}"
export SPA_BUCKET_NAME="${SPA_BUCKET_NAME:-""}"
export COMMIT_HASH="${COMMIT_HASH:-""}"
export WORKSPACE="${WORKSPACE:-""}"
export ARTEFACT_SUB_DIR="${ARTEFACT_SUB_DIR:-""}"
export ARTEFACT_BUCKET_NAME="${ARTEFACT_BUCKET_NAME:-""}"
export ENVIRONMENT="${ENVIRONMENT:-""}"

EXPORTS_SET=0
# Check key variables have been exported - see above


if [ -z "$FRONT_END_DIR" ] ; then
  echo Set FRONT_END_DIR to name of the front end directory
  EXPORTS_SET=1
fi

if [ -z "$SPA_BUCKET_NAME" ] ; then
  echo Set SPA_BUCKET_NAME to name of the bucket to hold the SPA
  EXPORTS_SET=1
fi

if [ -z "$COMMIT_HASH" ] ; then
  echo Set COMMIT_HASH to identify subfolder holding the deployable artefact
  EXPORTS_SET=1
fi

if [ -z "$WORKSPACE" ] ; then
  echo Set WORKSPACE to identify subfolder holding the deployable artefact
  EXPORTS_SET=1
fi

if [ -z "$ARTEFACT_BUCKET_NAME" ] ; then
  echo Set ARTEFACT_BUCKET_NAME to name of s3 bucket holding the deployable artefact
  EXPORTS_SET=1
fi

if [ -z "$ENVIRONMENT" ] ; then
  echo Set ENVIRONMENT to identify into which environment we are deploying the application
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
    echo One or more required exports not correctly set
    exit 1
fi

export DEPLOYMENT_FILE_NAME="build.zip"

if [ "$ENVIRONMENT" == 'prod' ] ; then
  # Copy to artefact released bucket and deploy from there
  aws s3 sync s3://ARTEFACT_BUCKET_NAME s3://${ARTEFACT_BUCKET_NAME}-released
  export ARTEFACT_BUCKET_NAME="${ARTEFACT_BUCKET_NAME}-released"
fi

# TODO can i pass file directly as zip-file parameter and avoid landing it in directory
# Navigate to the frontend directory if it exists
if [ -d "$FRONT_END_DIR" ]; then


  echo "Preparing to deploy react artefact to the ${WORKSPACE} workspace in the ${ENVIRONMENT} environment"
  cd "$FRONT_END_DIR"  || exit
  rm -rf temp
  mkdir temp

# TODO The if statements related to custom bucket locations should be refactored to be more elegant once we are happy this works

if [ -z "${ARTEFACT_SUB_DIR}" ]; then
echo "Downloading react artefact ${DEPLOYMENT_FILE_NAME} from ${ARTEFACT_BUCKET_NAME}/${WORKSPACE}/${COMMIT_HASH}"
  aws s3api get-object --bucket "${ARTEFACT_BUCKET_NAME}" --key "${WORKSPACE}/${COMMIT_HASH}/${DEPLOYMENT_FILE_NAME}" "${DEPLOYMENT_FILE_NAME}"
else
echo "Downloading react artefact ${DEPLOYMENT_FILE_NAME} from ${ARTEFACT_BUCKET_NAME}/${ARTEFACT_SUB_DIR}/${COMMIT_HASH}"
  aws s3api get-object --bucket "${ARTEFACT_BUCKET_NAME}" --key "${ARTEFACT_SUB_DIR}/${COMMIT_HASH}/${DEPLOYMENT_FILE_NAME}" "${DEPLOYMENT_FILE_NAME}"
echo "Note that a custom artefact lookup location has been specified as ${ARTEFACT_SUB_DIR} for this run."
fi

echo "Unpacking $DEPLOYMENT_FILE_NAME to temp folder"
unzip -d temp "${DEPLOYMENT_FILE_NAME}"
echo "Uploading files from unpacked $DEPLOYMENT_FILE_NAME to $SPA_BUCKET_NAME"
aws s3 sync temp s3://$SPA_BUCKET_NAME/
echo "Removing temp files"
rm -rf temp

# TODO The if statements related to custom bucket locations should be refactored to be more elegant once we are happy this works

if [ -z "${ARTEFACT_SUB_DIR}" ]; then
  echo "Tagging time of deployment to ${ENVIRONMENT} of artefact ${ARTEFACT_BUCKET_NAME}/${WORKSPACE}/${COMMIT_HASH}/${DEPLOYMENT_FILE_NAME}"
  DEPLOYED_AT=$(date '+%Y-%m-%d %H:%M:%S')
  aws s3api put-object-tagging \
      --bucket "${ARTEFACT_BUCKET_NAME}"  \
      --key "${WORKSPACE}/${COMMIT_HASH}/${DEPLOYMENT_FILE_NAME}" \
      --tagging "{\"TagSet\": [{ \"Key\": \"${ENVIRONMENT}\", \"Value\": \"${DEPLOYED_AT}\" }]}"
else
  echo "Tagging time of deployment to ${ENVIRONMENT} of artefact ${ARTEFACT_BUCKET_NAME}/${ARTEFACT_SUB_DIR}/${COMMIT_HASH}/${DEPLOYMENT_FILE_NAME}"
  DEPLOYED_AT=$(date '+%Y-%m-%d %H:%M:%S')
  aws s3api put-object-tagging \
      --bucket "${ARTEFACT_BUCKET_NAME}"  \
      --key "${ARTEFACT_SUB_DIR}/${COMMIT_HASH}/${DEPLOYMENT_FILE_NAME}" \
      --tagging "{\"TagSet\": [{ \"Key\": \"${ENVIRONMENT}\", \"Value\": \"${DEPLOYED_AT}\" }]}"
fi

else
  echo No frontend source code to deploy
fi
