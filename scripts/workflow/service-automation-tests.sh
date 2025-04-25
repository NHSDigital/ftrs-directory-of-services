#! /bin/bash

# This script runs service automation tests
#
export APPLICATION_TEST_DIR="${APPLICATION_TEST_DIR:-"tests/service_automation"}"

# check export has been done
EXPORTS_SET=0
if [ -z "$WORKSPACE" ] ; then
  echo Set WORKSPACE to the workspace to action the terraform in
  EXPORTS_SET=1
fi

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


if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

echo "Installing requirements"
pip install -r "$APPLICATION_TEST_DIR"/requirements.txt

echo "----------------------------------------------------------------------------------------------------------------------------------------------------"
echo "Now running $TEST_TAG automated tests under $APPLICATION_TEST_DIR for workspace $WORKSPACE and environment $ENVIRONMENT and tests of type $TEST_TYPE"

cd "$APPLICATION_TEST_DIR" || exit

if [ $TEST_TYPE = "ui" ] ; then
  pytest -s -m "$TEST_TAG" -p allure_pytest --alluredir=allure-results
fi


if [ $TEST_TYPE != "ui" ] ; then
  pytest -q -s -m "$TEST_TAG" -p allure_pytest_bdd --alluredir=allure-results
fi


TEST_RESULTS=$?

echo "Generating allure report"
allure generate --single-file -c -o  allure-reports;


if [ $TEST_RESULTS -ne 0 ] ; then
  echo "service automation tests have failed"
  exit $TEST_RESULTS
else
  echo "service automation tests have passed"
  exit 0
fi
