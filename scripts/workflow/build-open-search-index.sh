#!/usr/bin/env bash

# Fail on first error, treat unset vars as errors, and fail pipelines on pipe failures
set -euo pipefail
IFS=$'\n\t'

# Defaults and environment fallbacks
OPEN_SEARCH_DOMAIN="${OPEN_SEARCH_DOMAIN:-""}"
INDEX="${INDEX:-""}"
WORKSPACE="${WORKSPACE:-""}"
RETRY_MAX="${RETRY_MAX:-3}"
SIGN_WITH_AWS="${SIGN_WITH_AWS:-false}"
AWS_REGION="${AWS_REGION:-""}"
AWS_SERVICE="${AWS_SERVICE:-es}"

DRY_RUN=false
VERBOSE=false
WAIT_FOR_HEALTH=false
HEALTH_TIMEOUT=60

usage() {
  cat <<EOF
Usage: $0 [--index INDEX] [--domain DOMAIN] [--workspace WORKSPACE] [--dry-run] [--verbose] [--wait-for-health] [--health-timeout SECONDS]

Environment variables used as fallbacks: OPEN_SEARCH_DOMAIN, INDEX, WORKSPACE

Options:
  --index INDEX        Name of the index to create (or use INDEX env var)
  --domain DOMAIN      OpenSearch domain host (e.g. opensearch.example.com) (or use OPEN_SEARCH_DOMAIN env var)
  --workspace WORKSPACE Optional workspace suffix appended to index name (or use WORKSPACE env var)
  --dry-run            Show actions without performing network writes
  --verbose            Enable verbose output
  --wait-for-health    Wait until cluster health is at least 'yellow' before creating the index
  --health-timeout N   Timeout in seconds for wait-for-health (default: 60)
  -h, --help           Show this help message

Optional environment variables:
  SIGN_WITH_AWS=true   Use AWS SigV4 signing for requests (requires 'awscurl' installed and AWS credentials configured)
  AWS_REGION=region    AWS region to use when signing requests with awscurl (recommended when SIGN_WITH_AWS=true)
  AWS_SERVICE=service  AWS service name to sign for (default: es). Use 'aoss' for OpenSearch Serverless
EOF
  exit 2
}

# Simple logger with timestamps
log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }
log_info() { log "[INFO] $*"; }
log_warn() { log "[WARN] $*"; }
log_err() { log "[ERROR] $*"; }

# Parse CLI arguments (simple parser)
while [[ $# -gt 0 ]]; do
  case "$1" in
    --index)
      INDEX="$2"; shift 2;;
    --domain)
      OPEN_SEARCH_DOMAIN="$2"; shift 2;;
    --workspace)
      WORKSPACE="$2"; shift 2;;
    --dry-run)
      DRY_RUN=true; shift;;
    --verbose)
      VERBOSE=true; shift;;
    --wait-for-health)
      WAIT_FOR_HEALTH=true; shift;;
    --health-timeout)
      HEALTH_TIMEOUT="$2"; shift 2;;
    -h|--help)
      usage;;
    *)
      log_err "Unknown argument: $1"; usage;;
  esac
done

# Enable bash xtrace only when verbose requested
if [[ "$VERBOSE" == "true" ]]; then
  set -x
fi

# Validate required inputs
if [[ -z "${OPEN_SEARCH_DOMAIN}" ]]; then
  log_err "OPEN_SEARCH_DOMAIN is empty — please provide --domain or set OPEN_SEARCH_DOMAIN"
  usage
fi
if [[ -z "${INDEX}" ]]; then
  log_err "INDEX is empty — please provide --index or set INDEX"
  usage
fi

# Normalize WORKSPACE: trim whitespace, prefix with '-' if it doesn't start with '-' or '_', and validate allowed characters
if [[ -n "${WORKSPACE}" ]]; then
  # trim leading/trailing whitespace
  WORKSPACE="${WORKSPACE#${WORKSPACE%%[![:space:]]*}}"
  WORKSPACE="${WORKSPACE%${WORKSPACE##*[![:space:]]}}"

  # If it doesn't start with '-' or '_', prefix with '-'
  if [[ ! "${WORKSPACE}" =~ ^[-_] ]]; then
    WORKSPACE="-${WORKSPACE}"
  fi

  # Validate allowed characters: letters, digits, hyphen, underscore, dot
  if [[ ! "${WORKSPACE}" =~ ^[-_.A-Za-z0-9]+$ ]]; then
    log_err "WORKSPACE contains invalid characters; allowed: letters, digits, '-', '_', '.'"
    exit 2
  fi
fi

# Construct final index name (append workspace if present)
FINAL_INDEX="${INDEX}${WORKSPACE}"

log_info "Building OpenSearch Index: ${FINAL_INDEX} on OpenSearch Domain: ${OPEN_SEARCH_DOMAIN}"

# helper: check if awscurl is available when needed — but allow dry-run without awscurl
ensure_awscurl() {
  if [[ "${SIGN_WITH_AWS}" == "true" ]]; then
    if ! command -v awscurl >/dev/null 2>&1; then
      if [[ "${DRY_RUN}" == "true" ]]; then
        log_warn "SIGN_WITH_AWS=true but 'awscurl' not found; proceeding because this is a dry-run (network checks will be skipped)"
        return 1
      fi
      log_err "SIGN_WITH_AWS=true but 'awscurl' is not installed. Install with: pip install awscurl"
      exit 2
    fi
  fi
  return 0
}

# helper: check if index exists (returns 0 if exists)
index_exists() {
  local url="https://${OPEN_SEARCH_DOMAIN}/${FINAL_INDEX}"
  local status

  if [[ "${SIGN_WITH_AWS}" == "true" ]]; then
    # If awscurl is not available and we're in dry-run, treat as 'index not found' so dry-run continues
    if ! ensure_awscurl >/dev/null 2>&1; then
      return 1
    fi
    # Use awscurl to include SigV4 signed headers. We capture the HTTP status from response headers
    status=$(awscurl --service "${AWS_SERVICE}" ${AWS_REGION:+--region "${AWS_REGION}"} -X GET -i "${url}" 2>/dev/null | awk 'NR==1{print $2}' || echo "000")
  else
    status=$(curl -sS -o /dev/null -w "%{http_code}" --retry 2 --retry-delay 1 --connect-timeout 5 --max-time 30 "${url}" || echo "000")
  fi

  if [[ "$status" =~ ^2|^3 ]]; then
    return 0
  fi
  return 1
}

# helper: get cluster health status as 'green'/'yellow'/'red' (returns status string or empty on failure)
get_cluster_health() {
  local url="https://${OPEN_SEARCH_DOMAIN}/_cluster/health"
  local body
  if [[ "${SIGN_WITH_AWS}" == "true" ]]; then
    if ! ensure_awscurl >/dev/null 2>&1; then
      echo "";
      return 1
    fi
    body=$(awscurl --service "${AWS_SERVICE}" ${AWS_REGION:+--region "${AWS_REGION}"} -X GET "${url}" 2>/dev/null || true)
  else
    body=$(curl -sS --connect-timeout 5 --max-time 10 "${url}" || true)
  fi
  if [[ -z "${body}" ]]; then
    echo ""
    return 1
  fi
  # extract "status":"value"
  local status
  status=$(printf '%s' "${body}" | grep -oE '"status"\s*:\s*"[^"]+"' | head -n1 | sed -E 's/.*"status"\s*:\s*"([^"]+)".*/\1/')
  printf '%s' "${status}"
}

# helper: wait until health is at least yellow (or until timeout)
wait_for_health() {
  local timeout=${HEALTH_TIMEOUT:-60}
  local start
  start=$(date +%s)
  log_info "Waiting up to ${timeout}s for cluster health to be at least 'yellow'"
  while true; do
    local status
    status=$(get_cluster_health || true)
    if [[ -n "${status}" ]]; then
      log_info "Cluster health status: ${status}"
      if [[ "${status}" == "green" || "${status}" == "yellow" ]]; then
        log_info "Cluster health is ${status}; continuing"
        return 0
      fi
    else
      log_warn "Could not retrieve cluster health; will retry"
    fi
    local now
    now=$(date +%s)
    if (( now - start >= timeout )); then
      log_err "Timed out waiting for cluster health to become 'yellow' (timeout=${timeout}s)"
      return 1
    fi
    sleep 5
  done
}

# helper: perform network operation with retries and exponential backoff
curl_with_retry() {
  local -r max=${RETRY_MAX:-3}
  local i=1
  local status
  while true; do
    if [[ "${SIGN_WITH_AWS}" == "true" ]]; then
      # If awscurl missing and dry-run, return failure to allow dry-run path
      if ! ensure_awscurl >/dev/null 2>&1; then
        status="000"
      else
        # Use awscurl and capture HTTP status code from the first header line
        status=$(awscurl --service "${AWS_SERVICE}" ${AWS_REGION:+--region "${AWS_REGION}"} -X "$1" -i "$2" -H "Content-Type: application/json" -d "${3:-}" 2>/dev/null | awk 'NR==1{print $2}' || status="000")
      fi
    else
      # $1=method $2=url $3=payload
      status=$(curl -sS -o /dev/null -w "%{http_code}" --retry 0 --connect-timeout 5 --max-time 60 -X "$1" -H "Content-Type: application/json" -d "${3:-}" "$2" ) || status="000"
    fi

    if [[ "$status" =~ ^2|^3 ]]; then
      return 0
    fi
    if (( i >= max )); then
      log_err "Request failed after ${i} attempts (last status: ${status})"
      return 1
    fi
    log_warn "Request failed with status ${status}, retrying in $((i * 2))s... (attempt ${i}/${max})"
    sleep $((i * 2))
    i=$((i + 1))
  done
}

# The mapping/template payload — update as needed for your index
read -r -d '' INDEX_PAYLOAD <<'JSON' || true
{
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
}
JSON

# Dry-run: show what would be done
if [[ "$DRY_RUN" == "true" ]]; then
  log_info "DRY RUN: Would check existence of index '${FINAL_INDEX}' at https://${OPEN_SEARCH_DOMAIN}"
  if index_exists; then
    log_info "DRY RUN: Index '${FINAL_INDEX}' already exists — nothing to do"
  else
    log_info "DRY RUN: Would create index '${FINAL_INDEX}' with mapping:"
    printf '%s\n' "${INDEX_PAYLOAD}"
    if [[ "$WAIT_FOR_HEALTH" == "true" ]]; then
      log_info "DRY RUN: Would wait for cluster health to be at least 'yellow' (timeout=${HEALTH_TIMEOUT}s)"
    fi
  fi
  exit 0
fi

# Perform idempotent create: skip if exists
if index_exists; then
  log_info "Index '${FINAL_INDEX}' already exists on ${OPEN_SEARCH_DOMAIN}; skipping creation"
  exit 0
fi

# If requested, wait for health before attempting to create
if [[ "$WAIT_FOR_HEALTH" == "true" ]]; then
  if ! wait_for_health; then
    log_err "Cluster health did not reach acceptable state within ${HEALTH_TIMEOUT}s; aborting"
    exit 1
  fi
fi

# Create the index using PUT
create_index() {
  log_info "Creating index '${FINAL_INDEX}' on https://${OPEN_SEARCH_DOMAIN} (this may retry on transient failures)"
  local url="https://${OPEN_SEARCH_DOMAIN}/${FINAL_INDEX}"
  if curl_with_retry PUT "${url}" "${INDEX_PAYLOAD}"; then
    log_info "Index '${FINAL_INDEX}' created successfully"
    return 0
  else
    log_err "Failed to create index '${FINAL_INDEX}'"
    return 1
  fi
}

create_index
