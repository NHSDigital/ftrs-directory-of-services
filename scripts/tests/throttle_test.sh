#!/usr/bin/env bash
# Throttle/Rate-limit test harness (HTTP/2 + mTLS) using curl
#
# Example:
#   bash scripts/tests/throttle_test.sh \
#     -u "https://example" -a "<API_KEY>" -c /path/cert -k /path/key \
#     -p "k=v" -r 4 -d 30 --theory-rate 3 --theory-burst 9 -v \
#     --warmup 30 --json --out-log ./throttle.results.log

set -euo pipefail

# Tool metadata
TOOL_NAME="throttle-test"
TOOL_VERSION="1.2.0"
DEFAULT_UA="${TOOL_NAME}/${TOOL_VERSION}"

# Defaults
RATE=4            # requests per second to schedule
DURATION=30       # total seconds to run
METHOD="GET"
API_KEY=""
CERT=""
KEY=""
CA_BUNDLE=""
INSECURE=0
VERBOSE=0
URL=""
USER_AGENT="$DEFAULT_UA"
WARMUP=0         # seconds to idle before starting (refill token bucket)
AS_JSON=0
OUT_LOG=""
TEE_PATH=""
DRY_RUN=0
# theory values for expected first-429 calculation (token bucket)
THEORY_RATE=3
THEORY_BURST=9
# curl timeouts (seconds)
CURL_MAX_TIME=""           # if set, passed as --max-time
CURL_CONNECT_TIMEOUT=""    # if set, passed as --connect-timeout

PARAMS=()    # -p key=value (repeatable)
HEADERS=()   # -H "Key: Value" (repeatable)

# Portable fractional sleep using shell sleep only
fsleep() {
  sleep "$1"
}

# Require a command to be present
require_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "Error: required command '$1' not found in PATH" >&2; exit 127; }; }

usage() {
  cat <<EOF
Usage: $0 -u URL [-a API_KEY] [-c CERT -k KEY] [-C CA_BUNDLE | -I] \
          [-H "Key: Value"]... [-p key=value]... [-X METHOD] \
          [-r RATE] [-d DURATION] [--theory-rate N --theory-burst N] [-v] \
          [--max-time S] [--connect-timeout S] [--user-agent UA] \
          [--warmup S] [--json] [--out-log PATH]

Options:
  -u URL                  Target URL (without query if using -p)
  -a API_KEY              x-api-key value (or env API_KEY)
  -c CERT                 Client certificate (PEM) for mTLS (or env TLS_CERT)
  -k KEY                  Client private key (PEM) for mTLS (or env TLS_KEY)
  -C CA_BUNDLE            Custom CA bundle (PEM) for server verification (or env TLS_CA_BUNDLE)
  -I                      Insecure TLS (skip verification) [NOT recommended]
  -H "K: V"               Extra header (repeatable)
  -p key=value            Query param to url-encode (repeatable)
  -X METHOD               HTTP method (default GET)
  -r RATE                 Requests per second to schedule (default ${RATE})
  -d DURATION             Test duration in seconds (default ${DURATION})
  --theory-rate N         Configured API rate limit (default ${THEORY_RATE})
  --theory-burst N        Configured API burst limit (default ${THEORY_BURST})
  --max-time S            curl max total time per request (seconds)
  --connect-timeout S     curl connect timeout (seconds)
  --user-agent UA         Custom User-Agent (default ${DEFAULT_UA})
  --warmup S              Idle S seconds before sending (refill tokens)
  --json                  Print JSON summary in addition to human summary
  --out-log PATH          Write raw results to PATH (default: ./raw-results.log)
  --tee PATH              Also write the same console output to PATH (default: ./results.log)
  --dry-run              Simulate schedule and 200/429 outcomes; no network calls
  -v                      Verbose per-request log
  -h                      Help

Notes:
  - duration controls the scheduling window; total wall time ≈ warmup + duration + time for in-flight requests
EOF
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    -u) URL=$2; shift 2;;
    -a) API_KEY=$2; shift 2;;
    -c) CERT=$2; shift 2;;
    -k) KEY=$2; shift 2;;
    -C) CA_BUNDLE=$2; shift 2;;
    -I) INSECURE=1; shift;;
    -H) HEADERS+=("$2"); shift 2;;
    -p) PARAMS+=("$2"); shift 2;;
    -X) METHOD=$2; shift 2;;
    -r) RATE=$2; shift 2;;
    -d) DURATION=$2; shift 2;;
    --theory-rate) THEORY_RATE=$2; shift 2;;
    --theory-burst) THEORY_BURST=$2; shift 2;;
    --max-time) CURL_MAX_TIME=$2; shift 2;;
    --connect-timeout) CURL_CONNECT_TIMEOUT=$2; shift 2;;
    --user-agent) USER_AGENT=$2; shift 2;;
    --warmup) WARMUP=$2; shift 2;;
    --json) AS_JSON=1; shift;;
    --out-log) OUT_LOG=$2; shift 2;;
    --tee) TEE_PATH=$2; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    -v) VERBOSE=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2;;
  esac
done

# Env var defaults if flags not provided
CERT=${CERT:-${TLS_CERT:-}}
KEY=${KEY:-${TLS_KEY:-}}
CA_BUNDLE=${CA_BUNDLE:-${TLS_CA_BUNDLE:-}}

if [[ -z "$URL" ]]; then
  echo "Error: -u URL is required" >&2; usage; exit 2
fi

if { [[ -n "$CERT" ]] && [[ -z "$KEY" ]]; } || { [[ -z "$CERT" ]] && [[ -n "$KEY" ]]; }; then
  echo "Error: both -c CERT and -k KEY are required for mTLS" >&2; exit 2
fi

# Validate provided file paths (if any)
if [[ -n "$CERT" ]] && [[ ! -r "$CERT" ]]; then
  echo "Error: Client certificate file not found or unreadable: $CERT (cwd: $(pwd))" >&2; exit 2
fi
if [[ -n "$KEY" ]] && [[ ! -r "$KEY" ]]; then
  echo "Error: Client private key file not found or unreadable: $KEY (cwd: $(pwd))" >&2; exit 2
fi
if [[ -n "$CA_BUNDLE" ]] && [[ ! -r "$CA_BUNDLE" ]]; then
  echo "Error: CA bundle file not found or unreadable: $CA_BUNDLE (cwd: $(pwd))" >&2; exit 2
fi

# Validate numeric params
awk -v r="$RATE" 'BEGIN { exit (r>0)?0:1 }' || { echo "Error: -r RATE must be > 0 (got '$RATE')" >&2; exit 2; }
awk -v d="$DURATION" 'BEGIN { exit (d>0)?0:1 }' || { echo "Error: -d DURATION must be > 0 (got '$DURATION')" >&2; exit 2; }
awk -v w="$WARMUP" 'BEGIN { exit (w>=0)?0:1 }' || { echo "Error: --warmup must be >= 0 (got '$WARMUP')" >&2; exit 2; }
#if [[ -n "$HARD_STOP_GRACE" ]]; then awk -v g="$HARD_STOP_GRACE" 'BEGIN { exit (g>=0)?0:1 }' || { echo "Error: --hard-stop-grace must be >= 0 (got '$HARD_STOP_GRACE')" >&2; exit 2; }; fi

# Dependencies
require_cmd curl; require_cmd awk

# Derived values
TOTAL_REQ=$(awk -v r="$RATE" -v d="$DURATION" 'BEGIN { printf "%d", int(r*d) }')
SLEEP_STEP=$(awk -v r="$RATE" 'BEGIN { printf "%.6f", 1.0/r }')
TMPDIR=$(mktemp -d 2>/dev/null || mktemp -d -t throttle)
if [[ -n "$OUT_LOG" ]]; then
  mkdir -p "$(dirname "$OUT_LOG")"
  RAW_LOG="$OUT_LOG"
  : >"$RAW_LOG"
else
  RAW_LOG="./raw-results.log"
  : >"$RAW_LOG"
fi
# Default tee path if not provided
if [[ -z "$TEE_PATH" ]]; then
  TEE_PATH="./results.log"
fi
# Tee console output to file (overwrite each run) while still showing on console
mkdir -p "$(dirname "$TEE_PATH")" || true
: >"$TEE_PATH"
exec > >(tee "$TEE_PATH") 2>&1

# Build curl base args
CURL_ARGS=(-sS -o /dev/null -X "$METHOD" -A "$USER_AGENT")
# Add --http2 only if curl supports it
if curl -V 2>/dev/null | grep -qi "HTTP2"; then
  CURL_ARGS=(--http2 "${CURL_ARGS[@]}")
fi

# TLS verification
if [[ $INSECURE -eq 1 ]]; then
  CURL_ARGS+=(--insecure)
elif [[ -n "$CA_BUNDLE" ]]; then
  CURL_ARGS+=(--cacert "$CA_BUNDLE")
fi

# mTLS
if [[ -n "$CERT" && -n "$KEY" ]]; then
  CURL_ARGS+=(--cert "$CERT" --key "$KEY")
fi

# Timeouts
if [[ -n "$CURL_MAX_TIME" ]]; then CURL_ARGS+=(--max-time "$CURL_MAX_TIME"); fi
if [[ -n "$CURL_CONNECT_TIMEOUT" ]]; then CURL_ARGS+=(--connect-timeout "$CURL_CONNECT_TIMEOUT"); fi

# Headers
if [[ -n "$API_KEY" ]]; then CURL_ARGS+=(-H "x-api-key: $API_KEY"); fi
if (( ${#HEADERS[@]} > 0 )); then
  for h in "${HEADERS[@]}"; do CURL_ARGS+=(-H "$h"); done
fi

# Params
PARAM_ARGS=()
if (( ${#PARAMS[@]} > 0 )); then
  PARAM_ARGS=(-G)
  for p in "${PARAMS[@]}"; do PARAM_ARGS+=(--data-urlencode "$p"); done
fi

# Warm-up idle
if (( WARMUP > 0 )); then
  [[ $VERBOSE -eq 1 ]] && echo "Warming up (idle) for ${WARMUP}s to refill token bucket..."
  fsleep "$WARMUP"
fi

# Establish precise start time for scheduling (float if python3 available)
USE_FLOAT=0
if command -v python3 >/dev/null 2>&1; then
  START_EPOCH=$(python3 - <<'PY'
import time
print(f"{time.time():.6f}")
PY
)
  USE_FLOAT=1
else
  START_EPOCH=$(date +%s)
fi
export START_EPOCH USE_FLOAT

# Fire requests at scheduled offsets; launch curl as background near its slot
start_epoch_print=$(date +%s)
[[ $VERBOSE -eq 1 ]] && echo "Scheduling $TOTAL_REQ requests at ${RATE}/s over ${DURATION}s (sleep step ${SLEEP_STEP}s)"

for ((i=0; i< TOTAL_REQ; i++)); do
  offset=$(awk -v idx="$i" -v r="$RATE" 'BEGIN { printf "%.6f", idx/r }')
  (
    # Sleep until scheduled time relative to START_EPOCH
    if [[ "$USE_FLOAT" -eq 1 ]]; then
      now=$(python3 - <<'PY'
import time
print(f"{time.time():.6f}")
PY
)
      sleep_for=$(python3 - "$offset" "$START_EPOCH" "$now" <<'PY'
import sys
off=float(sys.argv[1])
start=float(sys.argv[2])
now=float(sys.argv[3])
st=off - (now - start)
print(f"{st if st>0 else 0.0:.6f}")
PY
)
      fsleep "$sleep_for"
    else
      elapsed=$(( $(date +%s) - START_EPOCH ))
      sleep_for=$(awk -v off="$offset" -v el="$elapsed" 'BEGIN{ st=off-el; if (st<0) st=0; printf "%.6f", st }')
      fsleep "$sleep_for"
    fi

    # Run curl or simulate
    if [[ $DRY_RUN -eq 1 ]]; then
      status=$(awk -v i="$i" -v r="$RATE" -v tr="$THEORY_RATE" -v b="$THEORY_BURST" 'BEGIN { tokens=b - i*(1.0 - tr/r); if (tokens>0) print 200; else print 429 }')
      ttime="0.000"
    else
      if (( ${#PARAM_ARGS[@]} > 0 )); then
        out=$(curl "${CURL_ARGS[@]}" "${PARAM_ARGS[@]}" --write-out '%{http_code} %{time_total}' "$URL" || true)
      else
        out=$(curl "${CURL_ARGS[@]}" --write-out '%{http_code} %{time_total}' "$URL" || true)
      fi
      status=${out%% *}; ttime=${out#* }
    fi
    [[ -z "$status" ]] && status="000"; [[ -z "$ttime" ]] && ttime="0"
    printf "%d %s %s\n" "$i" "$status" "$ttime" >> "$RAW_LOG"
    if [[ $VERBOSE -eq 1 ]]; then
      now_s=$(date +%s); rel=$(( now_s - start_epoch_print ))
      printf "i=%05d t=%4ds status=%s t_total=%ss\n" "$i" "$rel" "$status" "$ttime"
    fi
  ) &
done

wait || true

# Summarize
TOTAL=$(wc -l < "$RAW_LOG" | tr -d ' ')
FIRST_429_IDX=$(awk '$2=="429"{print $1; exit}' "$RAW_LOG" || true)
if [[ -n "$FIRST_429_IDX" ]]; then FIRST_429_SEC=$(awk -v idx="$FIRST_429_IDX" -v r="$RATE" 'BEGIN { printf "%.3f", idx/r }'); else FIRST_429_SEC=""; fi
COUNTS=$(awk '{c[$2]++} END {for (k in c) printf "%s %d\n", k, c[k]}' "$RAW_LOG" | sort)
EXPECTED_FIRST=""; awk -v r="$RATE" -v tr="$THEORY_RATE" 'BEGIN{exit !(r>tr)}' && EXPECTED_FIRST=$(awk -v burst="$THEORY_BURST" -v rps="$RATE" -v rate="$THEORY_RATE" 'BEGIN { printf "%.1f", burst/(rps-rate) }') || true

# Human summary
echo ""; echo "Summary:"; echo "  Total requests:   $TOTAL"
if [[ -n "$FIRST_429_SEC" ]]; then echo "  First 429 at:     ~${FIRST_429_SEC}s"; else echo "  First 429 at:     (none observed)"; fi
if [[ -n "$EXPECTED_FIRST" ]]; then echo "  Expected first 429 ~${EXPECTED_FIRST}s (rate=$THEORY_RATE, burst=$THEORY_BURST, rps=$RATE)"; fi
echo "  Status counts:"; echo "$COUNTS" | awk '{printf "    %s: %s\n", $1, $2}'
echo ""; echo "Raw log: $RAW_LOG (format: index status time_total_seconds)"
echo "Console log: $TEE_PATH"

# JSON summary (optional)
if [[ $AS_JSON -eq 1 ]]; then
  # Build a simple JSON without external tools
  echo "";
  echo "{";
  echo "  \"tool\": \"$TOOL_NAME\",";
  echo "  \"version\": \"$TOOL_VERSION\",";
  echo "  \"url\": \"$URL\",";
  echo "  \"method\": \"$METHOD\",";
  echo "  \"rps\": $RATE,";
  echo "  \"duration_seconds\": $DURATION,";
  echo "  \"theory_rate\": $THEORY_RATE,";
  echo "  \"theory_burst\": $THEORY_BURST,";
  if [[ -n "$EXPECTED_FIRST" ]]; then echo "  \"expected_first_429_seconds\": $EXPECTED_FIRST,"; else echo "  \"expected_first_429_seconds\": null,"; fi
  if [[ -n "$FIRST_429_SEC" ]]; then echo "  \"first_429_seconds\": $FIRST_429_SEC,"; else echo "  \"first_429_seconds\": null,"; fi
  echo "  \"raw_log\": \"$RAW_LOG\",";
  echo "  \"console_log\": \"$TEE_PATH\",";
  echo "  \"status_counts\": {";
  # Render counts
  sc_first=1; while read -r line; do
    code=$(echo "$line" | awk '{print $1}'); cnt=$(echo "$line" | awk '{print $2}');
    if [[ -n "$code" ]]; then
      if [[ $sc_first -eq 1 ]]; then sc_first=0; printf "    \"%s\": %s\n" "$code" "$cnt"; else printf ",   \"%s\": %s\n" "$code" "$cnt"; fi
    fi
  done <<< "$COUNTS"
  echo -n "  }"; echo "";
  echo "}"
fi
