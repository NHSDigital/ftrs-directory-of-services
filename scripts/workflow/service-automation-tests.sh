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

if [ -z "$COMMIT_HASH" ] && [ -z "$TAG" ]; then
  echo Set COMMIT_HASH or TAG
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

echo "----------------------------------------------------------------------------------------------------------------------------------------------------"
echo "Now running $TEST_TAG automated tests under $APPLICATION_TEST_DIR for workspace $WORKSPACE and environment $ENVIRONMENT and tests of type $TEST_TYPE"

cd "$APPLICATION_TEST_DIR" || exit

make test MARKERS="${TEST_TAG}" TEST_TYPE="${TEST_TYPE}" COMMIT_HASH="${TAG:-$COMMIT_HASH}"

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
