#!/bin/bash

#THIS SCRIPT EXECUTES THE RELEVANT DEPLOYMENT ACTIONS FOR THIS MICROSERVICE.
#IT IS REFERENCED BY THE APPLICATION PIPELINE AND THEREFORE MUST ALWAYS BE CALLED "deploy_service.sh"

# fail on first error
set -e
#INPUT ARGUMENTS
source ./scripts/functions/git-functions.sh

export SERVICE_NAME="${SERVICE_NAME:-""}"
echo "Service Name: ${SERVICE_NAME}"
echo "Deployment workspace ${DEPLOYMENT_WORKSPACE}"
export_terraform_workspace_name

FULL_SERVICE_NAME="${SERVICE_NAME}"

if [ "${TERRAFORM_WORKSPACE_NAME}" != "default" ]; then
  FULL_SERVICE_NAME="${FULL_SERVICE_NAME}-${TERRAFORM_WORKSPACE_NAME}"
fi

echo "Service Name Workspace: ${FULL_SERVICE_NAME}"
echo "Copy utility code"
# copy util code but not the test code
rsync -av --exclude='test/' ./application-utils/* ./application/"${SERVICE_NAME}"

cd ./application/"${SERVICE_NAME}"

zip -r deployment.zip .

LAMBDA_OUTPUT=$(aws lambda update-function-code --function-name="$FULL_SERVICE_NAME" --zip-file=fileb://deployment.zip --publish)
LATEST_VERSION=$(jq -r '.Version' --compact-output <<< "$LAMBDA_OUTPUT" )
PREVIOUS_VERSION=$(expr "$LATEST_VERSION" - 1)
echo "Latest version: ${LATEST_VERSION}"
echo "Previous version: ${PREVIOUS_VERSION}"
echo "Tidy up temporary files"
rm -rf ../../application/"${SERVICE_NAME}"/common/

#PLEASE NOTE THAT FOR EXPEDIENCY, THE COMMANDS BELOW SIMPLY UPDATE THE FUNCTION CODE AND PUBLISH A NEW VERSION.
#IN FUTURE, IT WOULD BE MORE APPROPRIATE TO BUILD AN IMAGE OF THE SERVICE, NAME IT WITH THE COMMIT HASH
#AND PUSH THE IMAGE TO AN ARTIFACT REGISTRY, BEFORE DEPLOYING THAT ARTIFACT

# if [ $ENVIRONMENT_NAME = 'staging' ]
# #FOR CERTAIN ENVIRONMENTS, WE MAY WANT TO USE A CANARY STYLE DEPLOYMENT WHERE TRAFFIC IS SPLIT BETWEEN THE NEW VERSION AN THE PREVIOUS VERSTION
# then
#     ROUTING_CONFIG=\'{"AdditionalVersionWeights" : {'"$LATEST_VERSION"' : 0.05} }\'
#     aws lambda update-alias --function-name=$SERVICE_NAME --name live-service --function-version $PREVIOUS_VERSION --routing-config '{"AdditionalVersionWeights" : {$PREVIOUS_VERSION : 0.05} }'
# else
#     aws lambda update-alias --function-name=$SERVICE_NAME --name live-service --function-version $LATEST_VERSION  --routing-config '{}'
# fi           #

