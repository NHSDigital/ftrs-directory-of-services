#! /bin/bash

# This script runs service automation tests
#
export APPLICATION_TEST_DIR="${APPLICATION_TEST_DIR:-"tests/service_automation"}"

# Handle WORKSPACE - unset if "default"
if [ "$WORKSPACE" = "default" ] ; then
  WORKSPACE=""
fi

# check export has been done
EXPORTS_SET=0
if [ -z "$APPLICATION_TEST_DIR" ] ; then
  echo Set APPLICATION_TEST_DIR to directory holding int test code
  EXPORTS_SET=1
fi

if [ -z "$ENVIRONMENT" ] ; then
  echo Set ENVIRONMENT
  EXPORTS_SET=1
fi

if [ -z "$TEST_TAG" ] ; then
  echo Set TEST_TAG
  EXPORTS_SET=1
fi

if [ -z "$TEST_TYPE" ] ; then
  echo Set TEST_TYPE
  EXPORTS_SET=1
fi

if [ -z "$API_NAME" ]; then
  echo "Set API_NAME (e.g., dos-search)"
  EXPORTS_SET=1
fi

if [ -z "$APIM_ENV" ]; then
  echo "Set APIM_ENV (e.g., internal-dev, internal-qa)"
  EXPORTS_SET=1
fi

if [ -z "$COMMIT_HASH" ] && [ -z "$TAG" ]; then
  echo Set COMMIT_HASH or TAG
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

echo "----------------------------------------------------------------------------------------------------------------------------------------------------"
echo "Now running APIM tests for API: $API_NAME in APIM environment: $APIM_ENV"
echo "Application test directory: $APPLICATION_TEST_DIR"
echo "Environment: $ENVIRONMENT"
echo "Workspace: $WORKSPACE"

# Step 1: Get Proxygen Access Token using existing script
echo "Step 1: Retrieving Proxygen access token..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "$SCRIPT_DIR/get-apim-token.sh"

export API_NAME="$API_NAME"
export ENV="$ENVIRONMENT"
PROXYGEN_ACCESS_TOKEN=$("$SCRIPT_DIR/get-apim-token.sh")

if [ -z "$PROXYGEN_ACCESS_TOKEN" ]; then
  echo "Error: Failed to retrieve Proxygen access token"
  exit 1
fi

echo "✓ Successfully retrieved Proxygen access token"

# Step 2: Use Proxygen Access Token to get APIGEE Access Token (pytest-nhsd-apim token)
echo "Step 2: Retrieving APIGEE access token from Proxygen API..."

PROXYGEN_BASE_URL="${PROXYGEN_BASE_URL:-$PROXYGEN_URL}"
if [ -z "$PROXYGEN_BASE_URL" ]; then
  echo "Error: PROXYGEN_BASE_URL or PROXYGEN_URL environment variable is required"
  exit 1
fi

PROXYGEN_BASE_URL="${PROXYGEN_BASE_URL%/}"
TOKEN_ENDPOINT="${PROXYGEN_BASE_URL}/apis/${API_NAME}/pytest-nhsd-apim-token"

echo "Fetching token from: $TOKEN_ENDPOINT"

APIGEE_TOKEN_RESPONSE=$(curl -fsS --request GET \
  --url "$TOKEN_ENDPOINT" \
  --header "Authorization: Bearer ${PROXYGEN_ACCESS_TOKEN}") || {
  echo "Error: Failed to retrieve APIGEE access token from Proxygen API"
  exit 1
}

# Extract the pytest_nhsd_apim_token from the response
APIGEE_ACCESS_TOKEN=$(echo "$APIGEE_TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('pytest_nhsd_apim_token', ''))")

if [ -z "$APIGEE_ACCESS_TOKEN" ]; then
  echo "Error: No pytest_nhsd_apim_token in response"
  echo "Response: $APIGEE_TOKEN_RESPONSE"
  exit 1
fi

export APIGEE_ACCESS_TOKEN="$APIGEE_ACCESS_TOKEN"
echo "✓ Successfully retrieved APIGEE access token"

# Step 3: Construct proxy name based on workspace
if [ -n "$WORKSPACE" ]; then
  # Workspaced proxy format: {api-name}--{apim-env}--{api-name}-{workspace}_FHIR_R4
  PROXY_NAME="${API_NAME}--${APIM_ENV}--${API_NAME}-${WORKSPACE}_FHIR_R4"
else
  # Default proxy format for main workspace: {api-name}--{apim-env}_FHIR_R4
  PROXY_NAME="${API_NAME}--${APIM_ENV}_FHIR_R4"
fi

echo "Using proxy name: $PROXY_NAME"

# Step 4: Run the APIM tests
echo "Step 3: Running APIM tests..."
cd "$APPLICATION_TEST_DIR" || exit

echo "----------------------------------------------------------------------------------------------------------------------------------------------------"
echo "Now running $TEST_TAG automated tests under $APPLICATION_TEST_DIR for workspace $WORKSPACE, environment $ENVIRONMENT,  proxy $PROXY_NAME and tests of type $TEST_TYPE"

make test MARKERS="${TEST_TAG}" TEST_TYPE="${TEST_TYPE}" COMMIT_HASH="${TAG:-$COMMIT_HASH}" API_NAME="${API_NAME}" PROXY_NAME="${PROXY_NAME}"


# echo "----------------------------------------------------------------------------------------------------------------------------------------------------"
# echo "Now running $TEST_TAG automated tests under $APPLICATION_TEST_DIR for workspace $WORKSPACE and environment $ENVIRONMENT and tests of type $TEST_TYPE"

# cd "$APPLICATION_TEST_DIR" || exit

# make test MARKERS="${TEST_TAG}" TEST_TYPE="${TEST_TYPE}" COMMIT_HASH="${TAG:-$COMMIT_HASH}"

TEST_RESULTS=$?



echo "Generating allure report"
make report

if [ $TEST_RESULTS -ne 0 ] ; then
  echo "service automation tests have failed"
  exit $TEST_RESULTS
else
  echo "service automation tests have passed"
  exit 0
fi
