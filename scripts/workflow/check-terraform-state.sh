#! /bin/bash

# fail on first error
set -e
EXPORTS_SET=0

# check necessary environment variables are set
if [ -z "$WORKSPACE" ] ; then
  echo Set WORKSPACE
  EXPORTS_SET=1
fi

if [ -z "$ENVIRONMENT" ] ; then
  echo Set ENVIRONMENT
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

export TF_VAR_repo_name="${REPOSITORY:-"$(basename -s .git "$(git config --get remote.origin.url)")"}"
export TERRAFORM_BUCKET_NAME="nhse-$ENVIRONMENT-$TF_VAR_repo_name-terraform-state"

echo "Checking for terraform workspace --> $WORKSPACE"
echo "Terraform state S3 bucket name being checked --> $TERRAFORM_BUCKET_NAME"

CLEARED=$(aws s3 ls s3://$TERRAFORM_BUCKET_NAME/env:/$WORKSPACE/ | awk '{print $2}')
if [ -n "$CLEARED" ] ; then
  echo "Not all state cleared - $CLEARED"
  exit 1
else
  echo All state entry for $WORKSPACE removed
fi
