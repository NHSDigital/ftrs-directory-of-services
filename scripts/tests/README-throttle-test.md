# Throttling Test (API Gateway)

A self-contained harness to validate AWS API Gateway throttling precisely (HTTP/2 + mTLS + fixed RPS pacing). It prints a clean summary and (optionally) a JSON report with the observed vs expected first-429 timing.

Key features

- Precise pacing: fixed RPS over a duration with minimal drift (portable fractional sleep)
- HTTP/2 when available, mTLS (cert+key), API key header, extra headers
- Query params via -p key=value (URL-encoded)
- Warm-up idle (refill tokens) before the test to start from a full bucket
- Deterministic raw log with optional custom path
- Human summary and optional JSON summary including expected first-429 time
- Robust file/path checks and macOS/BSD-friendly

Quick start (Bash)

```bash
chmod +x scripts/tests/throttle_test.sh
# 4 RPS for 30s (method 3/9 theory), verbose and JSON output with a custom log path
bash scripts/tests/throttle_test.sh \
  -u "https://your-endpoint" -a "<API_KEY>" -c /path/cert -k /path/key \
  -p "k=v" -r 4 -d 30 --theory-rate 3 --theory-burst 9 -v \
  --warmup 30 --json --out-log ./throttle.results.log
```

Environment defaults

- You can provide environment variables instead of flags: `API_KEY`, `TLS_CERT`, `TLS_KEY`, `TLS_CA_BUNDLE`
- Flags override environment variables when both are present

Important options

- -u URL: target URL (no query if using -p)
- -a API_KEY: x-api-key header (or environment variable `API_KEY`)
- -c/-k: client cert/key (PEM) for mTLS (or environment variables `TLS_CERT`/`TLS_KEY`)
- -C: custom CA bundle (PEM) or -I to skip verification (not recommended)
- -H / -p: extra headers and query params (repeatable)
- -r / -d: requests per second and duration in seconds
- --theory-rate / --theory-burst: print expected first-429 time for comparison
- --warmup S: idle S seconds before the test to refill tokens
- --json: also print a JSON summary (machine-readable)
- --out-log PATH: write the raw per-request results to PATH (default: ./raw-results.log)
- --tee PATH: also write the exact console output to PATH (default: ./results.log)
- --user-agent UA: set a custom User-Agent header for identification

When should 429s start? (Token-bucket reasoning)

- First 429 (approx.) = burst / (RPS − rate), assuming the bucket starts full and load is steady
- Examples for rate=3 and burst=9:
  - At 4 RPS: expected first 429 ≈ 9 / (4 − 3) = ~9s
  - At 12 RPS: expected first 429 ≈ 9 / (12 − 3) = ~1s
- For rate=150 and burst=450:
  - At 300 RPS: expected first 429 ≈ 450 / (300 − 150) = ~3s
  - To see ~6s at 300 RPS: set burst ≈ 900
  - To see ~4s at 300 RPS: set burst ≈ 600
- Alternatively, if you must keep rate=150 and burst=450, choose RPS for a target time T using:
  - RPS ≈ rate + (burst / T)
  - Target ~6s: RPS ≈ 150 + 450/6 = 225
  - Target ~4s: RPS ≈ 150 + 450/4 = 262.5 → use 262 or 263 RPS
- Start from idle so the bucket is full; expect small jitter (±0.5–1.5s)

Why you still see 200s after 429s

- Refill never stops: after the initial burst drains, the bucket refills at the configured rate (tokens/sec). As new tokens arrive, some in-flight requests succeed (200) and others fail (429); they interleave.
- Steady-state mix: approximate success fraction ≈ min(1, rate / RPS). Examples:
  - rate=3, RPS=4 → ~75% 200, ~25% 429 after the burst
  - rate=3, RPS=12 → ~25% 200, ~75% 429 after the burst
  - For rate=150:
    - At 300 RPS: success ≈ 150/300 → ~50% 200, ~50% 429 after the burst
    - At 200 RPS: success ≈ 150/200 → ~75% 200, ~25% 429 after the burst
- Multiple buckets: if both method-level and usage-plan throttles are set, the stricter one will cause 429s, but tokens in either bucket can refill moments later, allowing 200s to resume.
- Real-world jitter: distributed enforcement, per-node timing, and send-rate variance introduce small deviations from the exact ratio.

Testing method-level throttling vs usage plan throttling

- API Gateway applies both; the stricter one limits you
- Isolate method throttling: set method=3/9; set the usage plan at least 3x higher (e.g., 9/27)
  - For method=150/450, set the usage plan to at least 3× higher: rate ≈ 450 RPS, burst ≈ 1,350
  - If you plan spikes around 300 RPS during tests, keep the usage plan limits above that so the method remains the limiter (e.g., usage plan rate 600, burst 1,800 during performance tests)
- Test combined behavior: set both equal; onset matches the 3/9 theory (subject to small jitter)

Examples

- 4 RPS for 30s at method=3/9 (mTLS, verbose, JSON, warmup):

```bash
bash scripts/tests/throttle_test.sh \
  -u "https://dos-search-dosis-2264.dev.ftrs.cloud.nhs.uk/Organization" \
  -a "<API_KEY>" -c /path/cert -k /path/key \
  -p "_revinclude=Endpoint:organization" -p "identifier=odsOrganisationCode|H82028" \
  -r 4 -d 30 --theory-rate 3 --theory-burst 9 -v --warmup 30 --json
```

- Higher RPS to force early throttling (12 RPS, 10s):

```bash
bash scripts/tests/throttle_test.sh \
  -u "https://dos-search-dosis-2264.dev.ftrs.cloud.nhs.uk/Organization" \
  -a "<API_KEY>" -c /path/cert -k /path/key \
  -p "_revinclude=Endpoint:organization" -p "identifier=odsOrganisationCode|H82028" \
  -r 12 -d 10 --theory-rate 3 --theory-burst 9 -v
```

- Keep rate=150 and burst=450; choose RPS for target first-429 time:

```bash
# ~6s to first 429: RPS ≈ 225
make throttle-test \
  url="https://dos-search-dosis-2264.dev.ftrs.cloud.nhs.uk/Organization" \
  api_key="<API_KEY>" \
  cert=/Users/gurinderbrar/ca-cert key=/Users/gurinderbrar/ca-pk \
  params='_revinclude=Endpoint:organization' 'identifier=odsOrganisationCode|H82028' \
  rate=225 duration=10 theory_rate=150 theory_burst=450 verbose=true \
  max_time=10 connect_timeout=3

# ~4s to first 429: RPS ≈ 262–263
make throttle-test \
  url="https://dos-search-dosis-2264.dev.ftrs.cloud.nhs.uk/Organization" \
  api_key="<API_KEY>" \
  cert=/Users/gurinderbrar/ca-cert key=/Users/gurinderbrar/ca-pk \
  params='_revinclude=Endpoint:organization' 'identifier=odsOrganisationCode|H82028' \
  rate=263 duration=8 theory_rate=150 theory_burst=450 verbose=true \
  max_time=10 connect_timeout=3
```

Runtime control at high RPS (recommended)

- Duration (-d) controls the sending window; total wall time ≈ warmup + duration + time for in-flight requests to complete.
- For high RPS (hundreds/thousands of requests), there will be a “tail” as requests finish.
- If you need a strict total runtime near duration:

  - Manually interrupt around the desired time using Ctrl+C. Note: the script exits immediately and will not print the final summary, but raw-results.log will have per-request lines you can analyze.

  - Or use an OS-level timeout wrapper to stop the command after a fixed time (recommended for non-interactive runs):

```bash
# macOS: coreutils
brew install coreutils
# Run for ~10s total wall time
`gtimeout` 10s make throttle-test url="…" rate=300 duration=10 warmup=0

# Linux (GNU timeout)
`timeout` 10s make throttle-test url="…" rate=300 duration=10 warmup=0
```

- Script-only alternative: keep wall time close to duration by tightening per-request timeouts (may cause a few 000 timeouts under heavy load):

```bash
make throttle-test \
  url="https://dos-search-dosis-2264.dev.ftrs.cloud.nhs.uk/Organization" \
  api_key="<API_KEY>" \
  cert=$HOME/ca-cert key=$HOME/ca-pk \
  params='_revinclude=Endpoint:organization identifier=odsOrganisationCode|H82028' \
  rate=300 duration=10 warmup=0 theory_rate=150 theory_burst=450 \
  connect_timeout=3 max_time=6 verbose=false \
  tee=./results.log out_log=./raw-results.log
```

- Avoid Ctrl+Z (suspend); it pauses processes without finishing the run or summary. Ctrl+C aborts immediately and skips the summary.

JSON output example

```json
{
  "tool": "throttle-test",
  "version": "1.2.0",
  "url": "https://…/Organization",
  "method": "GET",
  "rps": 4,
  "duration_seconds": 30,
  "theory_rate": 3,
  "theory_burst": 9,
  "expected_first_429_seconds": 9.0,
  "first_429_seconds": 9.2,
  "raw_log": "./raw-results.log",
  "console_log": "./results.log",
  "status_counts": { "200": 90, "429": 30 }
}
```

Troubleshooting

- fork: Resource temporarily unavailable
  - You’re likely spawning more processes than the OS allows (very high RPS × duration)
  - Mitigations:
    - Lower `rate` and/or `duration` during experiments, then scale up gradually
    - Run with `verbose=false` to reduce console overhead
    - Consider using shorter `connect_timeout` to fail fast on connection pressure
    - Use the timeout wrapper above to cap wall time even if some curls linger
