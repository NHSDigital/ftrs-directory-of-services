#! /bin/bash
# You will need to export
# ACTION - The terraform action to perform, e.g. plan, apply, destroy, validate
# STACK - The infrastructure stack to action
# ENVIRONEMNT - The name of the environment to run the terraform action on, e.g. dev, test
# WORKSPACE - The name of the workspace to action the terraform into, e.g. DR-123
# REPOSITORY - The name of the repository to action the terraform on e.g. uec-dos-service-management

# fail on first error
set -e
# functions

export PROGRAM_CODE="${PROGRAM_CODE:-"nhse-uec"}"
export AWS_REGION="${AWS_REGION:-"eu-west-2"}"
export INFRASTRUCTURE_DIR="${INFRASTRUCTURE_DIR:-"infrastructure"}"
export TERRAFORM_DIR="${TERRAFORM_DIR:-"$INFRASTRUCTURE_DIR/stacks"}"
export ACTION="${ACTION:-""}"
export STACK="${STACK:-""}"
export ENVIRONMENT="${ENVIRONMENT:-""}"
export USE_REMOTE_STATE_STORE="${USE_REMOTE_STATE_STORE:-true}"
export PROJECT="${PROJECT:-"dos"}"
export TF_VAR_repo_name="${REPOSITORY:-"$(basename -s .git "$(git config --get remote.origin.url)")"}"
export TF_VAR_application_tag="${APPLICATION_TAG:-""}"
export TF_VAR_commit_hash="${COMMIT_HASH:-""}"

# needed for terraform management stack
export TF_VAR_terraform_state_bucket_name="nhse-$ENVIRONMENT-$TF_VAR_repo_name-terraform-state"  # globally unique name
export TF_VAR_terraform_lock_table_name="nhse-$ENVIRONMENT-$TF_VAR_repo_name-terraform-state-lock"

# check exports have been done
EXPORTS_SET=0
# Check key variables have been exported - see above
if [ -z "$ACTION" ] ; then
  echo Set ACTION to terraform action one of plan, apply, destroy, or validate
  EXPORTS_SET=1
fi

if [ -z "$STACK" ] ; then
  echo Set STACK to name of the stack to be actioned
  EXPORTS_SET=1
fi

if [ -z "$ENVIRONMENT" ] ; then
  echo Set ENVIRONMENT to the environment to action the terraform in - one of dev, test, preprod, prod
  EXPORTS_SET=1
else
  if [[ ! $ENVIRONMENT =~ ^(mgmt|dev|test|int|preprod|prod|security|prototype) ]]; then
      echo ENVIRONMENT should be mgmt dev test int preprod security or prod
      EXPORTS_SET=1
  fi
fi

if [ -z "$PROJECT" ] ; then
  echo Set PROJECT to dos or cm
  EXPORTS_SET=1
else
  if [[ ! "$PROJECT" =~ ^(dos|cm) ]]; then
      echo PROJECT should be dos or cm
      EXPORTS_SET=1
  fi
fi

if [ -z "$WORKSPACE" ] ; then
  echo Set WORKSPACE to the workspace to action the terraform in
  EXPORTS_SET=1
fi

if [ -z "$TF_VAR_repo_name" ] ; then
  echo Set REPOSITORY to the REPOSITORY to action the terraform in
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

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

COMMON_TF_VARS_FILE="common.tfvars"
STACK_TF_VARS_FILE="$STACK.tfvars"
ENV_TF_VARS_FILE="$ENVIRONMENT.tfvars"
ENVIRONMENTS_SUB_DIR="environments"

echo "Preparing to run terraform $ACTION for stack $STACK to terraform workspace $WORKSPACE for environment $ENVIRONMENT and project $PROJECT"
ROOT_DIR=$PWD
# the directory that holds the stack to terraform
STACK_DIR=$PWD/$TERRAFORM_DIR/$STACK
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

ENVIRONMENTS_DIR="$ROOT_DIR/$INFRASTRUCTURE_DIR/"

[ -d "$ROOT_DIR/$INFRASTRUCTURE_DIR/$ENVIRONMENTS_SUB_DIR" ]  && ENVIRONMENTS_DIR="$ENVIRONMENTS_DIR/$ENVIRONMENTS_SUB_DIR"
echo "Pulling environment variables from $ENVIRONMENTS_DIR"

# init terraform
terraform-initialise

if terraform workspace list | grep -qE "^\s*\*?\s*$WORKSPACE\s*$"; then
  echo "Workspace $WORKSPACE exists, selecting..."
  terraform workspace select "$WORKSPACE"
else
  if [ "$ACTION" = "destroy" ]; then
    echo "Workspace $WORKSPACE does not exist and action is destroy — nothing to destroy. Exiting gracefully."
    exit 0
  else
    echo "Workspace $WORKSPACE does not exist, creating..."
    terraform workspace new "$WORKSPACE"
  fi
fi

# plan
if [ -n "$ACTION" ] && [ "$ACTION" = 'plan' ] ; then
  terraform plan -out $STACK.tfplan \
    -var-file "$ROOT_DIR/$INFRASTRUCTURE_DIR/$COMMON_TF_VARS_FILE" \
    -var-file "$ROOT_DIR/$INFRASTRUCTURE_DIR/$STACK_TF_VARS_FILE" \
    -var-file "$ENVIRONMENTS_DIR/$ENV_TF_VARS_FILE"

  PLAN_RESULT=$(terraform show -no-color $STACK.tfplan)

  if [ -n "$GITHUB_WORKSPACE" ] ; then
    cp "$STACK.tfplan" "$GITHUB_WORKSPACE/$STACK.tfplan"

    # Look for the "No changes" string in the output for GitHub workflow.
    if echo "$PLAN_RESULT" | grep -Fq "No changes."; then
      INFRA_CHANGES="false"
    else
      INFRA_CHANGES="true"
      echo "plan_result=${INFRA_CHANGES}" >> "$GITHUB_OUTPUT"
      echo "Infra changes detected: ${INFRA_CHANGES}"
    fi
  fi
fi

if [ -n "$ACTION" ] && [ "$ACTION" = 'apply' ] ; then
  if [ -n "$GITHUB_WORKSPACE" ] ; then
      terraform apply -auto-approve "$GITHUB_WORKSPACE/$STACK.tfplan"
    else
      terraform apply -auto-approve "$STACK.tfplan"
  fi
fi

if [ -n "$ACTION" ] && [ "$ACTION" = 'destroy' ] ; then
  terraform destroy -auto-approve \
    -var-file "$ROOT_DIR/$INFRASTRUCTURE_DIR/$COMMON_TF_VARS_FILE" \
    -var-file "$ROOT_DIR/$INFRASTRUCTURE_DIR/$STACK_TF_VARS_FILE" \
    -var-file "$ENVIRONMENTS_DIR/$ENV_TF_VARS_FILE"
fi

if [ -n "$ACTION" ] && [ "$ACTION" = 'validate' ] ; then
  terraform validate
fi

# remove temp files
rm -f "$STACK_DIR"/locals.tf
rm -f "$STACK_DIR"/provider.tf
rm -f "$STACK_DIR"/versions.tf
rm -f "$STACK_DIR"/common-variables.tf

if [ $TEMP_STACK_TF_VARS_FILE = 1 ] ; then
  rm -f "$ROOT_DIR/$INFRASTRUCTURE_DIR/$STACK_TF_VARS_FILE"
fi

echo "Completed terraform $ACTION for stack $STACK to terraform workspace $WORKSPACE for account type $ENVIRONMENT and project $PROJECT"
