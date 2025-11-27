#!/usr/bin/env python3
"""Sanitize performance nfrs.yaml operations: replace None numeric fields with ''."""
from __future__ import annotations
from pathlib import Path
import sys
import yaml  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
PERF_YAML = ROOT / "requirements" / "nfrs" / "performance" / "nfrs.yaml"

def main() -> int:
    if not PERF_YAML.exists():
        print("performance/nfrs.yaml not found")
        return 0
    data = yaml.safe_load(PERF_YAML.read_text(encoding="utf-8")) or {}
    changed = False
    for n in data.get("nfrs", []) or []:
        for op in n.get("operations", []) or []:
            for key in ("p50_target_ms","p95_target_ms","absolute_max_ms","burst_tps_target","sustained_tps_target","max_request_payload_bytes"):
                if op.get(key) is None:
                    op[key] = ""
                    changed = True
    if changed:
        PERF_YAML.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        print("Sanitized None values in performance/nfrs.yaml operations")
    else:
        print("No sanitation needed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
