#!/usr/bin/env bash
set -euo pipefail

REPORT_DIR=${ALLURE_REPORT_DIR:-"tests/service_automation/allure-reports"}
BUCKET_NAME=${ARTEFACT_BUCKET_NAME:?"ARTEFACT_BUCKET_NAME is required"}
WORKSPACE_VALUE=${WORKSPACE:-}
COMMIT_VALUE=${COMMIT_HASH:-}

if [ -z "$WORKSPACE_VALUE" ] || [ "$WORKSPACE_VALUE" = "default" ]; then
  WORKSPACE_VALUE="default"
fi

if [ -z "$COMMIT_VALUE" ]; then
  COMMIT_VALUE="${GITHUB_SHA:-unknown}"
fi

if [ ! -d "$REPORT_DIR" ]; then
  echo "Allure report directory '$REPORT_DIR' not found, skipping S3 upload"
  exit 0
fi

TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
ZIP_DIR=$(mktemp -d)
trap 'rm -rf "$ZIP_DIR"' EXIT
ZIP_FILE="$ZIP_DIR/allure-report-${TIMESTAMP}.zip"

( cd "$REPORT_DIR" && zip -qr "$ZIP_FILE" . )

S3_KEY="${WORKSPACE_VALUE}/${COMMIT_VALUE}/service-automation/allure-report-${TIMESTAMP}.zip"

aws s3 cp "$ZIP_FILE" "s3://${BUCKET_NAME}/${S3_KEY}"

echo "Uploaded Allure report to s3://${BUCKET_NAME}/${S3_KEY}"
