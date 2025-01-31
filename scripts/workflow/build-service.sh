#!/bin/bash

# fail on first error
set -e

export SERVICE="${SERVICE:-""}"
echo "Building service: ${SERVICE}"

echo "Copy utility code"
# copy util code but not the test code
rsync -av --exclude='test/' ./application-utils/* ./"${DIRECTORY}"/"${SERVICE}"

cd ./"${DIRECTORY}"/"${SERVICE}"

zip -r "${SERVICE}".zip . -x "test*"

echo "Tidy up temporary files"
rm -rf ../../"${DIRECTORY}"/"${SERVICE}"/common/
