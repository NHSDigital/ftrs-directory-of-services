#!/usr/bin/env python3
"""
Stub validator for performance expectations.
    - Loads requirements/nfrs/performance/expectations.yaml
    - Generates synthetic latency samples per operation (or simulates breach via CLI)
    - Computes p50/p95 and compares to targets
    - Exits 0 on PASS, 1 on any violation

Usage:
  python3 scripts/perf/validate_perf_expectations.py --simulate
  python3 scripts/perf/validate_perf_expectations.py --simulate --breach triage-search

This is a stub; replace fetch_samples() with real metric ingestion when ready.
"""
import argparse
import random
import sys
from pathlib import Path

try:
    import yaml  # PyYAML is commonly available; if not, vendor later
except Exception:
    yaml = None

REGISTRY_PATH = Path('requirements/nfrs/performance/expectations.yaml')


def percentile(values, p):
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return float(s[int(k)])
    d0 = s[f] * (c - k)
    d1 = s[c] * (k - f)
    return float(d0 + d1)


def fetch_samples(op_id, target_p95, breach=False):
    """Generate synthetic samples centered under target, with optional breach."""
    samples = []
    base = target_p95 * (1.0 if breach else 0.6)
    for _ in range(250):  # modest sample size
        jitter = random.uniform(-0.2, 0.2) * target_p95
        samples.append(max(1.0, base + jitter))
    # enforce a few outliers
    for _ in range(5):
        samples.append(base + 0.5 * target_p95)
    return samples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--simulate', action='store_true', help='Use synthetic samples rather than real metrics')
    parser.add_argument('--breach', metavar='OPERATION_ID', help='Simulate p95 breach for a specific operation')
    args = parser.parse_args()

    if yaml is None:
        print('ERROR: PyYAML not available to parse expectations.yaml', file=sys.stderr)
        return 2

    if not REGISTRY_PATH.exists():
        print(f'ERROR: Registry file not found: {REGISTRY_PATH}', file=sys.stderr)
        return 2

    with REGISTRY_PATH.open() as f:
        cfg = yaml.safe_load(f)

    ops = cfg.get('operations', [])
    if not ops:
        print('ERROR: No operations found in expectations registry', file=sys.stderr)
        return 2

    violations = []
    for op in ops:
        op_id = op.get('operation_id')
        p50_target = int(op.get('p50_target_ms', 0))
        p95_target = int(op.get('p95_target_ms', 0))
        if p95_target <= 0 or p50_target <= 0:
            violations.append((op_id, 'schema', 'Targets must be positive integers'))
            continue
        breach = args.breach == op_id
        if args.simulate:
            samples = fetch_samples(op_id, p95_target, breach=breach)
        else:
            print('WARN: Non-simulated mode not implemented in stub; using synthetic samples')
            samples = fetch_samples(op_id, p95_target, breach=False)
        p50 = percentile(samples, 50)
        p95 = percentile(samples, 95)
        maxv = max(samples) if samples else 0
        if p50 > p50_target:
            violations.append((op_id, 'p50', round(p50, 1), p50_target))
        if p95 > p95_target:
            violations.append((op_id, 'p95', round(p95, 1), p95_target))
        abs_max = op.get('absolute_max_ms')
        if abs_max and maxv > int(abs_max):
            violations.append((op_id, 'max', round(maxv, 1), int(abs_max)))

    if violations:
        print('PERF VIOLATIONS:')
        for v in violations:
            print(' -', v)
        return 1
    print('Performance expectations satisfied (stub)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
