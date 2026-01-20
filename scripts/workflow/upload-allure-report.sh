#!/usr/bin/env bash
set -euo pipefail

REPORT_DIR=${ALLURE_REPORT_DIR:-"tests/service_automation/allure-reports"}
BUCKET_NAME=${ARTEFACT_BUCKET_NAME:?"ARTEFACT_BUCKET_NAME is required"}
WORKSPACE_VALUE=${WORKSPACE:-}
COMMIT_VALUE=${COMMIT_HASH:-}
DEPLOYMENT_TYPE=${DEPLOYMENT_TYPE:-"development"}
RELEASE_TAG=${RELEASE_TAG:-}
BRANCH=${BRANCH:-$(git rev-parse --abbrev-ref HEAD)}
RUN_TIMESTAMP=${RUN_TIMESTAMP:-$(date -u +"%Y-%m-%dT%H:%M:%SZ")}
RELEASE_VERSION=${RELEASE_VERSION:-$([ -n "$RELEASE_TAG" ] && echo "$RELEASE_TAG" || echo "null")}

# Function to generate build info JSON file
generate_build_info() {
  local build_info_file=$1
  local report_dir=$2

  mkdir -p "$(dirname "$build_info_file")"

  cat > "$build_info_file" <<EOF
{
  "git_commit": "$COMMIT_HASH",
  "run_timestamp": "$RUN_TIMESTAMP",
  "release_version": "$RELEASE_VERSION",
  "environment": "$ENVIRONMENT",
  "deployment_type": "$DEPLOYMENT_TYPE",
}
EOF

  echo "Generated build info: $build_info_file"
}

# Determine the deployment path based on deployment type
case "$DEPLOYMENT_TYPE" in
  development)
    if [ "$BRANCH" = "main" ]; then
      DEPLOYMENT_PATH="development/latest"
    else
      DEPLOYMENT_PATH="development/${WORKSPACE_VALUE}"
    fi
    ;;
  release-candidate)
    if [ -z "$RELEASE_TAG" ]; then
      echo "ERROR: RELEASE_TAG is required for release-candidate deployment type"
      exit 1
    fi
    DEPLOYMENT_PATH="release-candidates/$RELEASE_TAG"
    ;;
  release)
    if [ -z "$RELEASE_TAG" ]; then
      echo "ERROR: RELEASE_TAG is required for release deployment type"
      exit 1
    fi
    DEPLOYMENT_PATH="releases/$RELEASE_TAG"
    ;;
  *)
    echo "ERROR: Unknown DEPLOYMENT_TYPE '$DEPLOYMENT_TYPE'. Must be one of: development, release-candidate, release"
    exit 1
    ;;
esac

if [ -z "$WORKSPACE_VALUE" ] || [ "$WORKSPACE_VALUE" = "default" ]; then
  WORKSPACE_VALUE="default"
fi

if [ -z "$COMMIT_HASH" ]; then
  COMMIT_HASH="${GITHUB_SHA:-unknown}"
fi

if [ ! -d "$REPORT_DIR" ]; then
  echo "Allure report directory '$REPORT_DIR' not found, skipping S3 upload"
  exit 0
fi

TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
ZIP_DIR=$(mktemp -d)
trap 'rm -rf "$ZIP_DIR"' EXIT
ZIP_FILE="$ZIP_DIR/allure-report-${TIMESTAMP}.zip"
BUILD_INFO_FILE="$ZIP_DIR/build-info.json"

# Generate build info file
generate_build_info "$BUILD_INFO_FILE" "$REPORT_DIR"

# Create zip with report and build info
( cd "$REPORT_DIR" && zip -qr "$ZIP_FILE" "$REPORT_DIR" "$BUILD_INFO_FILE" )

S3_KEY="${DEPLOYMENT_PATH}/service-automation/${DEPLOYMENT_TYPE}/allure-report-${TIMESTAMP}.zip"

aws s3 cp "$ZIP_FILE" "s3://${BUCKET_NAME}/${S3_KEY}"

echo "Uploaded Allure report to s3://${BUCKET_NAME}/${S3_KEY}"
