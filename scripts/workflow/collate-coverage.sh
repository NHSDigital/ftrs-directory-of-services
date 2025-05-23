#! /bin/bash

# fail on first error
set -e
# # This script collates coverage reports for service level unit tests and produces a single coverage report
UNCOVERED_CODE=0
SERVICE_DIR=services
cd $SERVICE_DIR
echo Clear out previous collated coverage report if it exists
rm -f collated_service_coverage.xml

echo Create a new empty collated coverage report
touch collated_service_coverage.xml

echo Scanning for coverage in service sub directories

for f in */
do
  service_name=$(echo "$f" | tr "\/" '\n')
  if [ -e "$f/$service_name-coverage-summary.xml" ] ; then
    echo "Copying coverage report for $f to collated coverage report"
    cat "$f/$service_name-coverage-summary.xml" >> collated_service_coverage.xml
  else
    echo No coverage for "$f"
    UNCOVERED_CODE=1
  fi
done

if [ $UNCOVERED_CODE -eq 0 ] ; then
  echo All services have coverage
  exit 0
else
  echo Some services have no coverage
  # TODO - decide if we want to fail the build if there is incomplete coverage
  exit 0
fi
