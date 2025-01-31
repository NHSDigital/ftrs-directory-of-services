#! /bin/bash

PROGRAM_CODE="${PROGRAM_CODE:-"nhse-uec"}"
AWS_REGION="${AWS_REGION:-"eu-west-2"}"
INFRASTRUCTURE_DIR="${INFRASTRUCTURE_DIR:-"infrastructure"}"
TERRAFORM_DIR="${TERRAFORM_DIR:-"$INFRASTRUCTURE_DIR/stacks"}"
ENVIRONMENT="${ENVIRONMENT:-""}"
TF_VAR_repo_name="${TF_VAR_repo_name:-""}"

export TERRAFORM_BUCKET_NAME="nhse-$ENVIRONMENT-$TF_VAR_repo_name-terraform-state"  # globally unique name
export TERRAFORM_LOCK_TABLE="nhse-$ENVIRONMENT-$TF_VAR_repo_name-terraform-state-lock"

function terraform-initialise {
    STACK=$1
    ENVIRONMENT=$2
    TERRAFORM_USE_STATE_STORE=$3
    TERRAFORM_STATE_STORE=$TERRAFORM_BUCKET_NAME
    TERRAFORM_STATE_LOCK=$TERRAFORM_LOCK_TABLE
    TERRAFORM_STATE_KEY=$STACK/terraform.state

    echo "Terraform S3 State Bucket Name: ${TERRAFORM_BUCKET_NAME}"
    echo "Terraform Lock Table Name: ${TERRAFORM_LOCK_TABLE}"

    if [[ "$TERRAFORM_USE_STATE_STORE" =~ ^(false|no|n|off|0|FALSE|NO|N|OFF) ]]; then
      terraform init
    else
      terraform init \
          -backend-config="bucket=$TERRAFORM_STATE_STORE" \
          -backend-config="dynamodb_table=$TERRAFORM_STATE_LOCK" \
          -backend-config="encrypt=true" \
          -backend-config="key=$TERRAFORM_STATE_KEY" \
          -backend-config="region=$AWS_REGION"
    fi
}

function terraform-init-migrate {
    STACK=$1
    ENVIRONMENT=$2
    TERRAFORM_USE_STATE_STORE=$3
    TERRAFORM_STATE_STORE=$TERRAFORM_BUCKET_NAME
    TERRAFORM_STATE_LOCK=$TERRAFORM_LOCK_TABLE
    TERRAFORM_STATE_KEY=$STACK/terraform.state

    echo "Terraform S3 State Bucket Name: ${TERRAFORM_BUCKET_NAME}"
    echo "Terraform Lock Table Name: ${TERRAFORM_LOCK_TABLE}"

    terraform init -migrate-state -force-copy \
        -backend-config="bucket=$TERRAFORM_STATE_STORE" \
        -backend-config="dynamodb_table=$TERRAFORM_STATE_LOCK" \
        -backend-config="encrypt=true" \
        -backend-config="key=$TERRAFORM_STATE_KEY" \
        -backend-config="region=$AWS_REGION"

}
