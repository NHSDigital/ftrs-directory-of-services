#!/usr/bin/env sh
# Fetch a secret (whole or single key) from AWS Secrets Manager.
# Env vars:
#   SECRET_ID (required)
#   KEY       (optional; top-level or dotted for JSON)
#   MODE      (raw|json|kv) for whole-secret output; default raw
#   OUT       (optional file path)
#   AWS_REGION (optional)
#   VERBOSE   (optional; non-empty to print debug info to stderr)

set -eu

req() {
  printf '%s\n' "$1" >&2
}

: "${SECRET_ID:?SECRET_ID is required}"
MODE="${MODE:-raw}"
KEY_VAL="${KEY:-}"
OUT_VAL="${OUT:-}"
REGION_FLAG=""
[ -n "${AWS_REGION:-}" ] && REGION_FLAG="--region ${AWS_REGION}"

if ! command -v aws >/dev/null 2>&1; then
  req "aws CLI not found in PATH; install AWS CLI v2 and retry"
  exit 127
fi

if [ -n "${VERBOSE:-}" ]; then
  req "DEBUG secrets_get: SECRET_ID='${SECRET_ID}' KEY='${KEY_VAL}' MODE='${MODE}' OUT='${OUT_VAL}' REGION='${AWS_REGION:-}'"
fi

# Get the SecretString
RAW=""
if ! RAW=$(aws secretsmanager get-secret-value ${REGION_FLAG} --secret-id "${SECRET_ID}" --query SecretString --output text 2>/dev/null); then
  # Try to surface AWS CLI error
  ERR=$(aws secretsmanager get-secret-value ${REGION_FLAG} --secret-id "${SECRET_ID}" 2>&1 || true)
  req "AWS Secrets Manager error retrieving SecretString: ${ERR}"
  exit 1
fi

# If KEY provided, extract single value
if [ -n "${KEY_VAL}" ]; then
  # Trim leading whitespace to detect JSON vs key=value
  TRIM=$(printf '%s' "${RAW}" | sed 's/^[[:space:]]*//')
  VAL=""
  case "${TRIM}" in
    \{*|\[* )
      if ! command -v jq >/dev/null 2>&1; then
        req "jq is required to extract KEY from JSON SecretString. Install jq or omit KEY"
        exit 2
      fi
      # Support dotted path via jq getpath
      VAL=$(printf '%s' "${RAW}" | jq -r --arg k "${KEY_VAL}" 'getpath(($k | split("."))) // empty' 2>/dev/null || true)
      ;;
    * )
      # Fallback for simple key=value formatted secrets (first match wins)
      VAL=$(printf '%s\n' "${RAW}" | awk -v k="${KEY_VAL}" -F'=' '$1==k{print substr($0, index($0,$2)); exit}')
      ;;
  esac
  if [ -z "${VAL}" ] || [ "${VAL}" = "null" ]; then
    req "Key '${KEY_VAL}' not found or empty in secret '${SECRET_ID}'"
    exit 1
  fi
  if [ -n "${OUT_VAL}" ]; then
    printf '%s' "${VAL}" > "${OUT_VAL}"
    printf 'Wrote %s bytes to %s\n' "$(wc -c < "${OUT_VAL}")" "${OUT_VAL}" >&2
  else
    printf '%s\n' "${VAL}"
  fi
  exit 0
fi

# Whole secret output modes
case "${MODE}" in
  raw)
    OUTSTR="${RAW}"
    ;;
  json)
    if ! command -v jq >/dev/null 2>&1; then
      req "jq is required for MODE=json"
      exit 2
    fi
    OUTSTR=$(printf '%s' "${RAW}" | jq .)
    ;;
  kv)
    if ! command -v jq >/dev/null 2>&1; then
      req "jq is required for MODE=kv"
      exit 2
    fi
    OUTSTR=$(printf '%s' "${RAW}" | jq -r 'to_entries | .[] | "\(.key)=\(.value)"')
    ;;
  *)
    req "Invalid MODE='${MODE}'. Use raw|json|kv"
    exit 2
    ;;
esac

if [ -n "${OUT_VAL}" ]; then
  printf '%s' "${OUTSTR}" > "${OUT_VAL}"
  printf 'Wrote %s bytes to %s\n' "$(wc -c < "${OUT_VAL}")" "${OUT_VAL}" >&2
else
  printf '%s\n' "${OUTSTR}"
fi
