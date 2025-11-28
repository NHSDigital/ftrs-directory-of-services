
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

OPEN_SEARCH_DOMAIN=${OPEN_SEARCH_DOMAIN:-}
INDEX=${INDEX:-}
WORKSPACE=${WORKSPACE:-}
AWS_REGION=${AWS_REGION:-}
AWS_SERVICE=${AWS_SERVICE:-aoss}

err(){ printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }
[ -n "$OPEN_SEARCH_DOMAIN" ] || { err "ERROR: OPEN_SEARCH_DOMAIN not set"; exit 2; }
[ -n "$INDEX" ] || { err "ERROR: INDEX not set"; exit 2; }

err "AWS_REGION: ${AWS_REGION:-<unset>}"
if [ -n "${AWS_DEFAULT_REGION:-}" ]; then
  err "AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION}"
fi

if command -v aws >/dev/null 2>&1; then
  AWS_CLI_VERSION=$(aws --version 2>&1 || true)
  err "aws CLI: ${AWS_CLI_VERSION}"

  STS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>&1 || true)
  STS_ARN=$(aws sts get-caller-identity --query Arn --output text 2>&1 || true)

  if [[ "${STS_ACCOUNT}" =~ ^[0-9]+$ ]]; then
    err "AWS account: ${STS_ACCOUNT}"
    err "AWS caller ARN: ${STS_ARN}"
  else
    err "AWS account: unavailable"
    exit 3
  fi
else
  err "aws CLI not found"
  exit 4
fi

resolve_serverless_collection(){
  local name="$1" region_arg aws_json id endpoint
  region_arg=${2:+--region "$2"}

  id=$(aws opensearchserverless list-collections --query "collectionSummaries[?name=='${name}'].id | [0]" --output text 2>/dev/null || true)
  if [[ -z "$id" || "$id" == "None" ]]; then
    return 1
  fi

  endpoint=$(aws opensearchserverless batch-get-collection --ids "$id" --query 'collectionDetails[0].collectionEndpoint' --output text 2>/dev/null || true)
  if [[ -z "$endpoint" || "$endpoint" == "None" ]]; then
    endpoint=$(aws opensearchserverless batch-get-collection --ids "$id" --query 'collectionDetails[0].endpoint' --output text 2>/dev/null || true)
  fi

  if [[ -n "$endpoint" && "$endpoint" != "None" ]]; then
    printf '%s' "$endpoint"
    return 0
  fi
  return 1
}

if [[ "$OPEN_SEARCH_DOMAIN" != *.* ]]; then
  err "Resolving serverless collection '${OPEN_SEARCH_DOMAIN}' via AWS API"
  RESOLVED=$(resolve_serverless_collection "$OPEN_SEARCH_DOMAIN" "$AWS_REGION" || true)
  if [[ -n "$RESOLVED" ]]; then
    OPEN_SEARCH_DOMAIN=${RESOLVED#https://}
    err "AWS lookup found endpoint: ${OPEN_SEARCH_DOMAIN}"
  else
    err "ERROR: could not resolve serverless collection '${OPEN_SEARCH_DOMAIN}'"
    exit 2
  fi
fi

OPEN_SEARCH_DOMAIN=${OPEN_SEARCH_DOMAIN#https://}
if [[ -n "$WORKSPACE" && "${WORKSPACE:0:1}" != "-" ]]; then WORKSPACE="-$WORKSPACE"; fi
FINAL_INDEX="${INDEX}${WORKSPACE}"

PAYLOAD='{
  "mappings": {
    "properties": {
      "primary_key": {"type": "keyword"},
      "sgsd": {
        "type": "nested",
        "properties": {
          "sg": {"type": "integer"},
          "sd": {"type": "integer"}
        }
      }
    }
  }
}'

URL="https://${OPEN_SEARCH_DOMAIN}/${FINAL_INDEX}"
URL=$(echo "${URL}" | tr -d '\n\r')
err "Final URL: ${URL}"

TMP_PAYLOAD_FILE=$(mktemp /tmp/os-payload-XXXXXX.json)
printf '%s' "${PAYLOAD}" > "${TMP_PAYLOAD_FILE}"
err "Payload written to ${TMP_PAYLOAD_FILE}"

if command -v awscurl >/dev/null 2>&1; then
  err "Using awscurl to create index"
  AWSCURL_STDOUT=$(mktemp /tmp/awscurl-out-XXXXXX)
  AWSCURL_STDERR=$(mktemp /tmp/awscurl-err-XXXXXX)

  set +e
  err "Invoking awscurl: service=${AWS_SERVICE} region=${AWS_REGION:-<unset>}"
  err "AWS env creds present: AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:+yes:-no} AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:+yes:-no} AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN:+yes:-no}"

  awscurl --verbose --service "${AWS_SERVICE}" ${AWS_REGION:+--region "${AWS_REGION}"} \
    --fail-with-body -X PUT -H "Content-Type: application/json" \
    --data-binary @"${TMP_PAYLOAD_FILE}" "${URL}" >"${AWSCURL_STDOUT}" 2>"${AWSCURL_STDERR}"
  AWSCURL_RC=$?
  set -e

  if [ -s "${AWSCURL_STDOUT}" ]; then
    err "awscurl stdout (first 4k):"
    head -c 4096 "${AWSCURL_STDOUT}" | sed -n '1,200p' >&2 || true
  fi
  if [ -s "${AWSCURL_STDERR}" ]; then
    err "awscurl stderr (first 4k):"
    head -c 4096 "${AWSCURL_STDERR}" | sed -n '1,200p' >&2 || true
  fi

  if [ ${AWSCURL_RC} -ne 0 ]; then
    err "awscurl returned non-zero exit code ${AWSCURL_RC}. This indicates a request or signing error."
    err "Caller ARN (from STS): ${STS_ARN}"
    rm -f "${TMP_PAYLOAD_FILE}" "${AWSCURL_STDOUT}" "${AWSCURL_STDERR}"
    exit 7
  else
    err "awscurl succeeded"
    rm -f "${AWSCURL_STDOUT}" "${AWSCURL_STDERR}"
  fi
else
  err "awscurl not found. Install it or use Python SigV4 signing."
  rm -f "${TMP_PAYLOAD_FILE}"
  exit 2
fi

rm -f "${TMP_PAYLOAD_FILE}"
err "Index ${FINAL_INDEX} created (or already exists) on ${OPEN_SEARCH_DOMAIN}"
