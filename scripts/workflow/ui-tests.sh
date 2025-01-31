#! /bin/bash

# This script runs playwright cucumber ui tests
#
export AWS_REGION="${AWS_REGION:-""}"     # The aws region

APPLICATION_TEST_DIR='tests/ui'


# check export has been done
EXPORTS_SET=0

if [ -z "$AWS_REGION" ] ; then
  echo Set AWS_REGION
  EXPORTS_SET=1
fi

if [ -z "$ENVIRONMENT" ] ; then
  echo Set ENVIRONMENT
  EXPORTS_SET=1
fi

if [ -z "$WORKSPACE" ] ; then
  echo Set WORKSPACE
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

cd $APPLICATION_TEST_DIR || exit
echo "Installing requirements"
npm ci
npx playwright install --with-deps

echo "Running ui tests"
WORKSPACE=$WORKSPACE ENV=$ENVIRONMENT REGION=$AWS_REGION npm run test_pipeline

TEST_RESULTS=$?

echo "set up allure environment properties file"
echo "Branch = $TERRAFORM_WORKSPACE_NAME" > allure-results/environment.properties

echo "next generating report"
allure generate --single-file -c -o  allure-reports;

if [ $TEST_RESULTS -ne 0 ] ; then
  echo "UI Tests have failed"
  exit $TEST_RESULTS
else
  echo "UI Unit Tests have passed"
  exit 0
fi
