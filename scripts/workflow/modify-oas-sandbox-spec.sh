#!/bin/bash

set -euo pipefail

: "${API_NAME:?API_NAME environment variable is required}"
: "${PROXY_ENV:?PROXY_ENV environment variable is required}"
: "${VERSION_TAG:?VERSION_TAG environment variable is required}"

if ! command -v yq >/dev/null 2>&1; then
    sudo apt-get update >/dev/null
    sudo apt-get install -y yq >/dev/null
fi

ORIGINAL_TARGET_SPEC="docs/specification/x-nhsd-apim/target-sandbox-${API_NAME}.yaml"
SPEC_FILE="docs/specification/${API_NAME}-sandbox.yaml"

if [[ ! -f "$ORIGINAL_TARGET_SPEC" ]]; then
    echo "Error: Spec file not found at $ORIGINAL_TARGET_SPEC" >&2
    echo "Current directory: $(pwd)" >&2
    exit 1
fi

if [[ ! -f "$SPEC_FILE" ]]; then
    echo "Error: Spec file not found at $SPEC_FILE" >&2
    echo "Current directory: $(pwd)" >&2
    exit 1
fi

if [[ "$PROXY_ENV" == "sandbox" ]]; then
    SPEC_FILE_TMP=$(mktemp "$(dirname "$SPEC_FILE")/${API_NAME}-servers-trimmed.XXXXXX.yaml") || {
        echo "Error: Unable to create temporary sandbox spec file" >&2
        exit 1
    }
    cp "$SPEC_FILE" "$SPEC_FILE_TMP"
    yq eval -i 'del(.servers[0])' "$SPEC_FILE_TMP"
    SPEC_FILE="$SPEC_FILE_TMP"
fi

TARGET_SPEC_TMP=$(mktemp "$(dirname "$ORIGINAL_TARGET_SPEC")/target-sandbox.${API_NAME}.XXXXXX") || {
    echo "Error: Unable to create temporary target spec file" >&2
    exit 1
}
TARGET_SPEC_FILE="${TARGET_SPEC_TMP}.yaml"
mv "$TARGET_SPEC_TMP" "$TARGET_SPEC_FILE"
cp "$ORIGINAL_TARGET_SPEC" "$TARGET_SPEC_FILE"

yq eval -i '.containers[0].image.tag = env(VERSION_TAG)' \
    "$TARGET_SPEC_FILE"

if ! MODIFIED_SPEC_PATH_TMP=$(mktemp "$(dirname "$SPEC_FILE")/${API_NAME}-sandbox.XXXXXX"); then
    echo "Error: Unable to create temporary sandbox spec JSON" >&2
    exit 1
fi
MODIFIED_SPEC_PATH="${MODIFIED_SPEC_PATH_TMP}.json"
mv "$MODIFIED_SPEC_PATH_TMP" "$MODIFIED_SPEC_PATH"

env TARGET_SPEC_FILE_PATH="$TARGET_SPEC_FILE" \
    yq eval -o=json '."x-nhsd-apim".target = load(strenv(TARGET_SPEC_FILE_PATH))' \
    "$SPEC_FILE" > "$MODIFIED_SPEC_PATH"

printf '%s\n%s\n' "$MODIFIED_SPEC_PATH" "$TARGET_SPEC_FILE"
