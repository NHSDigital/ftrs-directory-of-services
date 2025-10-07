#!/usr/bin/env bash
set -euo pipefail

# Optional debug: set DEBUG=1 to trace commands
if [[ "${DEBUG:-0}" == "1" ]]; then set -x; fi

BASE_URL=${BASE_URL:-http://localhost:9000}
accept_hdr="Accept: application/fhir+json"
# Optional: wait up to WAIT_SECS for service to become ready (/_status). 0 means no wait.
WAIT_SECS=${WAIT_SECS:-0}

pass() { echo "PASS - $1"; }
fail() { echo "FAIL - $1"; exit 1; }

wait_ready() {
  local deadline=$(( $(date +%s) + WAIT_SECS ))
  while true; do
    if curl -fsS "$BASE_URL/_status" >/dev/null 2>&1; then
      return 0
    fi
    if (( WAIT_SECS == 0 )); then
      echo "Service not reachable at $BASE_URL/_status. Start the container or set BASE_URL to a running endpoint." >&2
      return 1
    fi
    if (( $(date +%s) >= deadline )); then
      echo "Timed out waiting for $BASE_URL/_status after ${WAIT_SECS}s" >&2
      return 1
    fi
    sleep 1
  done
}

do_call() {
  local path="$1"
  local expect_status="$2"
  local label="$3"

  http_code=$(curl -s -o /tmp/smoke_out.json -w "%{http_code}" -H "$accept_hdr" "${BASE_URL}${path}") || true

  if [[ "$http_code" != "$expect_status" ]]; then
    echo "--- Response body ---"
    cat /tmp/smoke_out.json || true
    echo "----------------------"
    fail "${label}: expected ${expect_status}, got ${http_code} for ${path}"
  fi
  pass "${label} (${expect_status})"
}

# Preflight: ensure target is reachable (optionally wait)
wait_ready

# 1) 200 success
do_call "/Organization?identifier=odsOrganisationCode%7CABC123&_revinclude=Endpoint:organization" 200 "200 success (identifier + _revinclude)"

# 2) 400 invalid-identifier-system
do_call "/Organization?identifier=foo%7CABC123&_revinclude=Endpoint:organization" 400 "400 invalid-identifier-system"

# 3) 400 invalid-identifier-value
do_call "/Organization?identifier=odsOrganisationCode%7CABC&_revinclude=Endpoint:organization" 400 "400 invalid-identifier-value"

# 4) 400 missing-revinclude
do_call "/Organization?identifier=odsOrganisationCode%7CABC123" 400 "400 missing-revinclude"

echo "All smoke tests passed against ${BASE_URL}"
