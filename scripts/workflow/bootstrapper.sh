#! /bin/bash

# This bootstrapper script initialises various resources necessary for Terraform and Github Actions to build
# the DoS or CM application in an AWS account
# fail on first error
set -e
# Before running this bootstrapper script:
#  - Login to an appropriate AWS account as appropriate user via commamnd-line AWS-cli
#  - Export the following variables appropriate for your account and github setup prior to calling this script
#  - They are NOT set in this script to avoid details being stored in repo
export ACTION="${ACTION:-"plan"}"                 # default action is plan
export AWS_REGION="${AWS_REGION:-""}"                             # The AWS region into which you intend to deploy the application (where the terraform bucket will be created) eg eu-west-2
export ENVIRONMENT="${ENVIRONMENT:-""}"                    # Identify the environment (one of dev,test,security,preprod or prod) usually part of the account name
export PROJECT="${PROJECT:-"dos"}"
export TF_VAR_repo_name="${REPOSITORY:-"$(basename -s .git "$(git config --get remote.origin.url)")"}"
export TF_VAR_terraform_state_bucket_name="nhse-$ENVIRONMENT-$TF_VAR_repo_name-terraform-state"  # globally unique name
export TF_VAR_terraform_lock_table_name="nhse-$ENVIRONMENT-$TF_VAR_repo_name-terraform-state-lock"

export WORKSPACE="${WORKSPACE:-"default"}"

# These used by both stacks to be bootstrapped
ROOT_DIR=$PWD
COMMON_TF_VARS_FILE="common.tfvars"
INFRASTRUCTURE_DIR="${INFRASTRUCTURE_DIR:-"infrastructure"}"
TERRAFORM_DIR="${TERRAFORM_DIR:-"$INFRASTRUCTURE_DIR/stacks"}"
ENVIRONMENTS_DIR="$ROOT_DIR/$INFRASTRUCTURE_DIR/environments"
# Github org
export TF_VAR_github_org="NHSDigital"
# check exports have been done
EXPORTS_SET=0
# Check key variables have been exported - see above
if [[ ! "$ACTION" =~ ^(plan|apply|destroy) ]]; then
    echo ACTION must be one of following terraform actions - plan, apply or destroy
    EXPORTS_SET=1
fi

if [ -z "$AWS_REGION" ] ; then
  echo Set AWS_REGION to name of the AWS region to host the terraform state bucket
  EXPORTS_SET=1
fi

if [ -z "$PROJECT" ] ; then
  echo Set PROJECT to identify if account is for dos or cm
  EXPORTS_SET=1
else
  if [[ ! "$PROJECT" =~ ^(dos|cm) ]]; then
      echo PROJECT should be dos or cm
      EXPORTS_SET=1
  fi
fi

if [ -z "$ENVIRONMENT" ] ; then
  echo Set ENVIRONMENT to identify if account is for dev, test, security, preprod or prod
  EXPORTS_SET=1
else
  if [[ ! $ENVIRONMENT =~ ^(mgmt|dev|test|int|preprod|prod|security|prototype) ]]; then
      echo ENVIRONMENT should be mgmt dev test int preprod security or prod
      EXPORTS_SET=1
  fi
fi

if [ $EXPORTS_SET = 1 ] ; then
    echo One or more required exports not correctly set
    exit 1
fi

ENV_TF_VARS_FILE="$ENVIRONMENT.tfvars"
if ! [ -f "$ENVIRONMENTS_DIR/$ENV_TF_VARS_FILE" ] ; then
  echo "No environment variables defined for $ENVIRONMENT environment"
  exit 1
fi


# -------------
# First time thru we haven't build the remote state bucket or lock table - so assume it doesn't exist to use
# if remote state bucket does exist we are going to use it
if aws s3api head-bucket --bucket "$TF_VAR_terraform_state_bucket_name" 2>/dev/null; then
  echo "Terraform S3 State Bucket Name: ${TF_VAR_terraform_state_bucket_name} already bootstrapped"
  export USE_REMOTE_STATE_STORE=true
else
  export USE_REMOTE_STATE_STORE=false
fi

# ------------- Step one create tf state bucket, state locks and account alias -----------
export ACTION=$ACTION
export STACK=terraform_management

# function to migrate state from local to remote
function terraform-init-migrate {
    TERRAFORM_STATE_KEY=$STACK/terraform.state

    terraform init -migrate-state -force-copy \
        -backend-config="bucket=$TF_VAR_terraform_state_bucket_name" \
        -backend-config="dynamodb_table=$TF_VAR_terraform_lock_table_name" \
        -backend-config="encrypt=true" \
        -backend-config="key=$TERRAFORM_STATE_KEY" \
        -backend-config="region=$AWS_REGION"

}
# function to determine if state is held locally or remote
function terraform-initialise {

    echo "Terraform S3 State Bucket Name: ${TF_VAR_terraform_state_bucket_name}"
    echo "Terraform Lock Table Name: ${TF_VAR_terraform_lock_table_name}"

    if [[ "$USE_REMOTE_STATE_STORE" =~ ^(false|no|n|off|0|FALSE|NO|N|OFF) ]]; then
      terraform init
    else
      terraform init \
          -backend-config="bucket=$TF_VAR_terraform_state_bucket_name" \
          -backend-config="dynamodb_table=$TF_VAR_terraform_lock_table_name" \
          -backend-config="encrypt=true" \
          -backend-config="key=$STACK/terraform.state" \
          -backend-config="region=$AWS_REGION"
    fi
}

function github_runner_stack {
    #  now do account_wide stack for github runner and for oidc provider
  export STACK=github_runner
  # specific to stack
  STACK_TF_VARS_FILE="$STACK.tfvars"
  # the directory that holds the stack to terraform
  STACK_DIR=$PWD/$TERRAFORM_DIR/$STACK

  if [[ "$USE_REMOTE_STATE_STORE" =~ ^(false|no|n|off|0|FALSE|NO|N|OFF) ]]; then
    echo "Bootstrapping the $STACK stack (terraform $ACTION) to terraform workspace $WORKSPACE for environment $ENVIRONMENT and project $PROJECT"
  else
    echo "Preparing to run terraform $ACTION for $STACK stack to terraform workspace $WORKSPACE for environment $ENVIRONMENT and project $PROJECT"
  fi

  # remove any previous local backend for stack
  rm -rf "$STACK_DIR"/.terraform
  rm -f "$STACK_DIR"/.terraform.lock.hcl
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/common/locals.tf "$STACK_DIR"
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/common/provider.tf "$STACK_DIR"
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/common/common-variables.tf "$STACK_DIR"
  #  copy shared tf files to stack
  if [[ "$USE_REMOTE_STATE_STORE" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON) ]]; then
    cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/remote/versions.tf "$STACK_DIR"
  else
    cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/local/versions.tf "$STACK_DIR"
  fi
  # switch to target stack directory ahead of tf init/plan/apply
  cd "$STACK_DIR" || exit
  # if no stack tfvars create temporary one
  TEMP_STACK_TF_VARS_FILE=0
  if [ ! -f "$ROOT_DIR/$INFRASTRUCTURE_DIR/$STACK_TF_VARS_FILE" ] ; then
    touch "$ROOT_DIR/$INFRASTRUCTURE_DIR/$STACK_TF_VARS_FILE"
    TEMP_STACK_TF_VARS_FILE=1
  fi

  # init terraform
  terraform-initialise

  if [ -n "$ACTION" ] && [ "$ACTION" = 'plan' ] ; then
    terraform plan \
    -var-file "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/$COMMON_TF_VARS_FILE \
    -var-file "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/$STACK_TF_VARS_FILE \
    -var-file "$ENVIRONMENTS_DIR/$ENV_TF_VARS_FILE"
  fi

  if [ -n "$ACTION" ] && [ "$ACTION" = 'apply' ] ; then
    terraform apply -auto-approve \
    -var-file "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/$COMMON_TF_VARS_FILE \
    -var-file "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/$STACK_TF_VARS_FILE \
    -var-file "$ENVIRONMENTS_DIR/$ENV_TF_VARS_FILE"
  fi
  # cleardown temp files
  rm -f "$STACK_DIR"/common-variables.tf
  rm -f "$STACK_DIR"/locals.tf
  rm -f "$STACK_DIR"/provider.tf
  rm -f "$STACK_DIR"/versions.tf
  if [[ $TEMP_STACK_TF_VARS_FILE == 1 ]]; then
    rm "$ROOT_DIR/$INFRASTRUCTURE_DIR/$STACK_TF_VARS_FILE"
  fi

}

if [[ "$USE_REMOTE_STATE_STORE" =~ ^(false|no|n|off|0|FALSE|NO|N|OFF) ]]; then
  echo "Bootstrapping the $STACK stack (terraform $ACTION) to terraform workspace $WORKSPACE for environment $ENVIRONMENT and project $PROJECT"
else
  echo "Preparing to run terraform $ACTION for $STACK stack to terraform workspace $WORKSPACE for environment $ENVIRONMENT and project $PROJECT"
fi

# specific to stack
STACK_TF_VARS_FILE="$STACK.tfvars"
# the directory that holds the stack to terraform
STACK_DIR=$PWD/$TERRAFORM_DIR/$STACK
# remove any previous local backend for stack
rm -rf "$STACK_DIR"/.terraform
rm -f "$STACK_DIR"/.terraform.lock.hcl
#  copy shared tf files to stack
cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/common/locals.tf "$STACK_DIR"
cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/common/provider.tf "$STACK_DIR"
cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/common/common-variables.tf "$STACK_DIR"

if [[ "$USE_REMOTE_STATE_STORE" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON) ]]; then
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/remote/versions.tf "$STACK_DIR"
else
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/local/versions.tf "$STACK_DIR"
fi
# switch to target stack directory ahead of tf init/plan/apply
cd "$STACK_DIR" || exit
# if no stack tfvars create temporary one
TEMP_STACK_TF_VARS_FILE=0
if [ ! -f "$ROOT_DIR/$INFRASTRUCTURE_DIR/$STACK_TF_VARS_FILE" ] ; then
  touch "$ROOT_DIR/$INFRASTRUCTURE_DIR/$STACK_TF_VARS_FILE"
  TEMP_STACK_TF_VARS_FILE=1
fi

# init terraform
terraform-initialise

if [ -n "$ACTION" ] && [ "$ACTION" = 'plan' ] ; then
  terraform plan \
  -var-file "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/$COMMON_TF_VARS_FILE \
  -var-file "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/$STACK_TF_VARS_FILE \
  -var-file "$ENVIRONMENTS_DIR/$ENV_TF_VARS_FILE"
fi
if [ -n "$ACTION" ] && [ "$ACTION" = 'apply' ] ; then
  terraform apply -auto-approve \
  -var-file "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/$COMMON_TF_VARS_FILE \
  -var-file "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/$STACK_TF_VARS_FILE \
  -var-file "$ENVIRONMENTS_DIR/$ENV_TF_VARS_FILE"
fi
if [ -n "$ACTION" ] && [ "$ACTION" = 'destroy' ] ; then
  terraform destroy -auto-approve \
  -var-file "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/$COMMON_TF_VARS_FILE \
  -var-file "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/$STACK_TF_VARS_FILE \
  -var-file "$ENVIRONMENTS_DIR/$ENV_TF_VARS_FILE"
fi
# cleardown temp files
rm -f "$STACK_DIR"/common-variables.tf
rm -f "$STACK_DIR"/locals.tf
rm -f "$STACK_DIR"/provider.tf
rm -f "$STACK_DIR"/versions.tf

if [[ $TEMP_STACK_TF_VARS_FILE == 1 ]]; then
  rm "$ROOT_DIR/$INFRASTRUCTURE_DIR/$STACK_TF_VARS_FILE"
fi

# back to root
cd "$ROOT_DIR" || exit

# having build the stack using a local backend we need to migrate the state held locally to newly build remote

if ! $USE_REMOTE_STATE_STORE  ; then
  # check if remote state bucket exists we are okay to migrate state to it
  if aws s3api head-bucket --bucket "$TF_VAR_terraform_state_bucket_name" 2>/dev/null; then
    export USE_REMOTE_STATE_STORE=true
    echo Preparing to migrate stack from local backend to remote backend
    # the directory that holds the stack to terraform
    ROOT_DIR=$PWD
    STACK_DIR=$PWD/$TERRAFORM_DIR/$STACK
    cd "$STACK_DIR" || exit
    cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/remote/versions.tf "$STACK_DIR"
    cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/common/locals.tf "$STACK_DIR"
    cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/common/provider.tf "$STACK_DIR"
    # run terraform init with migrate flag set
    terraform-init-migrate
    # now push local state to remote
    terraform state push "$STACK_DIR"/terraform.tfstate
    rm -f "$STACK_DIR"/locals.tf
    rm -f "$STACK_DIR"/provider.tf
    rm -f "$STACK_DIR"/versions.tf
    # remove local terraform state to prevent clash when re-running eg to plan
    rm -f "$STACK_DIR"/terraform.tfstate
    cd "$ROOT_DIR" || exit
  else
    export USE_REMOTE_STATE_STORE=false
  fi
fi

# back to root
cd "$ROOT_DIR" || exit
echo "Preparing the $TF_VAR_repo_name repo github-runner in $ENVIRONMENT environment"
github_runner_stack

