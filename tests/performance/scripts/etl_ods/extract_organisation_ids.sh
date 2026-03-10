#!/usr/bin/env bash
set -euo pipefail

# Extract organisation identifiers from DynamoDB for CRUD performance tests.
#
# Usage:
#   ENVIRONMENT=dev ./scripts/extract_organisation_ids.sh
#   ENVIRONMENT=dev WORKSPACE=my-branch LIMIT=100 ./scripts/extract_organisation_ids.sh
#
# Required:  ENVIRONMENT (dev|test|int|ref)
# Optional:  WORKSPACE (default: "default"), LIMIT, AWS_REGION, OUTPUT_FILE

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PERF_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

: "${ENVIRONMENT:?ENVIRONMENT must be set (dev|test|int|ref)}"

AWS_REGION="${AWS_REGION:-eu-west-2}"
WORKSPACE="${WORKSPACE:-default}"
LIMIT="${LIMIT:-}"
OUTPUT_FILE="${OUTPUT_FILE:-${PERF_DIR}/parameter_files/crud_organisation_ids.csv}"

# Convention: ftrs-dos-{env}-database-organisation{-workspace}
TABLE_NAME="ftrs-dos-${ENVIRONMENT}-database-organisation"
[[ "${WORKSPACE}" != "default" ]] && TABLE_NAME="${TABLE_NAME}-${WORKSPACE}"

echo "Scanning ${TABLE_NAME} (${AWS_REGION}), limit: ${LIMIT:-all}"

mkdir -p "$(dirname "${OUTPUT_FILE}")"
echo "org_id,org_odscode,org_name" > "${OUTPUT_FILE}"

SCAN_ARGS=(
    dynamodb scan
    --region "${AWS_REGION}"
    --table-name "${TABLE_NAME}"
    --projection-expression "id, identifier_ODS_ODSCode, #n"
    --expression-attribute-names '{"#n":"name"}'
    --output json
)

[[ -n "${LIMIT}" ]] && SCAN_ARGS+=(--max-items "${LIMIT}")

TOTAL=0
TOKEN=""

while :; do
    CMD=(aws "${SCAN_ARGS[@]}")
    [[ -n "${TOKEN}" ]] && CMD+=(--starting-token "${TOKEN}")

    RESPONSE=$("${CMD[@]}")

    # Parse DynamoDB JSON items → CSV rows; count written to temp file
    COUNT_FILE=$(mktemp)
    echo "${RESPONSE}" | python3 -c "
import sys, json, csv

data = json.load(sys.stdin)
items = data.get('Items', [])
writer = csv.writer(sys.stdout, quoting=csv.QUOTE_MINIMAL)
count = 0
for item in items:
    org_id = item.get('id', {}).get('S', '')
    ods_code = item.get('identifier_ODS_ODSCode', {}).get('S', '')
    name = item.get('name', {}).get('S', '')
    if org_id:
        writer.writerow([org_id, ods_code, name])
        count += 1
print(count, file=sys.stderr)
" >> "${OUTPUT_FILE}" 2>"${COUNT_FILE}"

    BATCH=$(cat "${COUNT_FILE}" 2>/dev/null || echo "0")
    rm -f "${COUNT_FILE}"
    TOTAL=$((TOTAL + BATCH))
    echo "  Fetched ${TOTAL} organisations so far..."

    TOKEN=$(echo "${RESPONSE}" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("NextToken",""))')

    [[ -z "${TOKEN}" ]] && break
    [[ -n "${LIMIT}" && "${TOTAL}" -ge "${LIMIT}" ]] && break
done

echo "Extracted ${TOTAL} organisations → ${OUTPUT_FILE}"
